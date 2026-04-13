(define-constant contract-owner tx-sender)

(define-constant err-unauthorized (err u100))
(define-constant err-not-found (err u101))
(define-constant err-invalid-status (err u102))
(define-constant err-invalid-input (err u103))
(define-constant err-review-closed (err u104))
(define-constant err-consensus-required (err u105))

(define-constant review-status-pending u0)
(define-constant review-status-in-progress u1)
(define-constant review-status-completed u2)

(define-data-var next-review-id uint u1)
(define-data-var next-regimen-id uint u1)
(define-data-var next-session-id uint u1)
(define-data-var next-outcome-id uint u1)

(define-map authorized-pharmacists principal bool)

(define-map medication-reviews
  uint
  {
    patient: principal,
    pharmacist: principal,
    review-date: uint,
    status: uint,
    finalized-at: uint,
    decision: (string-ascii 256),
    last-finding-id: uint,
    last-recommendation-id: uint
  }
)

(define-map clinical-findings
  { review-id: uint, finding-id: uint }
  { content: (string-ascii 256), created-at: uint }
)

(define-map recommendations
  { review-id: uint, recommendation-id: uint }
  {
    content: (string-ascii 256),
    pharmacist-approved: bool,
    pharmacist-approved-at: uint,
    patient-approved: bool,
    patient-approved-at: uint
  }
)

(define-map drug-interactions
  { drug-a: uint, drug-b: uint }
  {
    severity: uint,
    significance: (string-ascii 120),
    management: (string-ascii 256),
    evidence-level: uint,
    updated-at: uint
  }
)

(define-map therapy-regimens
  uint
  {
    patient: principal,
    pharmacist: principal,
    current-meds: (list 20 uint),
    proposed-meds: (list 20 uint),
    goals: (string-ascii 256),
    status: uint,
    implemented: bool,
    created-at: uint,
    implemented-at: uint
  }
)

(define-map regimen-approvals
  uint
  { pharmacist-approved: bool, patient-approved: bool }
)

(define-map counseling-sessions
  uint
  {
    patient: principal,
    pharmacist: principal,
    topics: (string-ascii 256),
    materials: (string-ascii 256),
    follow-up-required: bool,
    session-date: uint,
    understanding-score: uint,
    documented: bool
  }
)

(define-map clinical-outcomes
  uint
  {
    patient: principal,
    regimen-id: uint,
    metric-type: (string-ascii 64),
    measurement: uint,
    assessed-at: uint,
    target-achieved: bool,
    flagged: bool
  }
)

(define-map adherence-scores
  { patient: principal, regimen-id: uint }
  { score: uint, updated-at: uint }
)

(define-map patient-stats
  principal
  { reviews: uint, regimens: uint, sessions: uint, outcomes: uint, issues: uint }
)

(define-private (is-owner (who principal))
  (is-eq who contract-owner)
)

(define-private (is-pharmacist (who principal))
  (default-to false (map-get? authorized-pharmacists who))
)

(define-private (assert-owner)
  (if (is-owner tx-sender) (ok true) err-unauthorized)
)

(define-private (assert-pharmacist)
  (if (is-pharmacist tx-sender) (ok true) err-unauthorized)
)

(define-private (has-dual-recommendation-approval (item { content: (string-ascii 256), pharmacist-approved: bool, pharmacist-approved-at: uint, patient-approved: bool, patient-approved-at: uint }))
  (and (get pharmacist-approved item) (get patient-approved item))
)

(define-private (has-dual-regimen-approval (approval { pharmacist-approved: bool, patient-approved: bool }))
  (and (get pharmacist-approved approval) (get patient-approved approval))
)

(define-private (can-transition-review-status (current-status uint) (next-status uint))
  (or
    (and (is-eq current-status review-status-pending) (is-eq next-status review-status-in-progress))
    (and (is-eq current-status review-status-in-progress) (is-eq next-status review-status-in-progress))
  )
)

(define-private (get-stats (patient principal))
  (default-to
    { reviews: u0, regimens: u0, sessions: u0, outcomes: u0, issues: u0 }
    (map-get? patient-stats patient)
  )
)

(define-private (bump-review-count (patient principal))
  (let ((stats (get-stats patient)))
    (map-set patient-stats patient (merge stats { reviews: (+ (get reviews stats) u1) }))
  )
)

(define-private (bump-regimen-count (patient principal))
  (let ((stats (get-stats patient)))
    (map-set patient-stats patient (merge stats { regimens: (+ (get regimens stats) u1) }))
  )
)

(define-private (bump-session-count (patient principal))
  (let ((stats (get-stats patient)))
    (map-set patient-stats patient (merge stats { sessions: (+ (get sessions stats) u1) }))
  )
)

(define-private (bump-outcome-count (patient principal))
  (let ((stats (get-stats patient)))
    (map-set patient-stats patient (merge stats { outcomes: (+ (get outcomes stats) u1) }))
  )
)

(define-private (bump-issue-count (patient principal))
  (let ((stats (get-stats patient)))
    (map-set patient-stats patient (merge stats { issues: (+ (get issues stats) u1) }))
  )
)

(define-public (authorize-pharmacist (who principal))
  (begin
    (try! (assert-owner))
    (ok (map-set authorized-pharmacists who true))
  )
)

(define-public (revoke-pharmacist (who principal))
  (begin
    (try! (assert-owner))
    (ok (map-delete authorized-pharmacists who))
  )
)

(define-public (create-medication-review (patient principal) (review-date uint))
  (let
    (
      (review-id (var-get next-review-id))
      (review
        {
          patient: patient,
          pharmacist: tx-sender,
          review-date: review-date,
          status: review-status-pending,
          finalized-at: u0,
          decision: "",
          last-finding-id: u0,
          last-recommendation-id: u0
        }
      )
    )
    (begin
      (try! (assert-pharmacist))
      (map-set medication-reviews review-id review)
      (var-set next-review-id (+ review-id u1))
      (bump-review-count patient)
      (ok review-id)
    )
  )
)

(define-public (update-review-status (review-id uint) (status uint))
  (let ((review (unwrap! (map-get? medication-reviews review-id) err-not-found)))
    (begin
      (try! (assert-pharmacist))
      (asserts! (is-eq (get pharmacist review) tx-sender) err-unauthorized)
      (asserts! (can-transition-review-status (get status review) status) err-invalid-status)
      (map-set medication-reviews review-id (merge review { status: status }))
      (ok true)
    )
  )
)

(define-public (add-clinical-finding (review-id uint) (content (string-ascii 256)))
  (let ((review (unwrap! (map-get? medication-reviews review-id) err-not-found)))
    (begin
      (try! (assert-pharmacist))
      (asserts! (not (is-eq (get status review) review-status-completed)) err-review-closed)
      (asserts! (is-eq (get pharmacist review) tx-sender) err-unauthorized)
      (let ((finding-id (+ (get last-finding-id review) u1)))
        (map-set clinical-findings { review-id: review-id, finding-id: finding-id } { content: content, created-at: block-height })
        (map-set medication-reviews review-id (merge review { last-finding-id: finding-id }))
        (ok finding-id)
      )
    )
  )
)

(define-public (propose-recommendation (review-id uint) (content (string-ascii 256)))
  (let ((review (unwrap! (map-get? medication-reviews review-id) err-not-found)))
    (begin
      (try! (assert-pharmacist))
      (asserts! (not (is-eq (get status review) review-status-completed)) err-review-closed)
      (asserts! (is-eq (get pharmacist review) tx-sender) err-unauthorized)
      (let ((recommendation-id (+ (get last-recommendation-id review) u1)))
        (map-set recommendations { review-id: review-id, recommendation-id: recommendation-id } { content: content, pharmacist-approved: false, pharmacist-approved-at: u0, patient-approved: false, patient-approved-at: u0 })
        (map-set medication-reviews review-id (merge review { last-recommendation-id: recommendation-id }))
        (ok recommendation-id)
      )
    )
  )
)

(define-public (approve-recommendation (review-id uint) (recommendation-id uint))
  (let
    (
      (review (unwrap! (map-get? medication-reviews review-id) err-not-found))
      (item (unwrap! (map-get? recommendations { review-id: review-id, recommendation-id: recommendation-id }) err-not-found))
    )
    (begin
      (asserts! (not (is-eq (get status review) review-status-completed)) err-review-closed)
      (asserts! (or (is-eq tx-sender (get pharmacist review)) (is-eq tx-sender (get patient review))) err-unauthorized)
      (if
        (is-eq tx-sender (get pharmacist review))
        (map-set recommendations { review-id: review-id, recommendation-id: recommendation-id } (merge item { pharmacist-approved: true, pharmacist-approved-at: block-height }))
        (map-set recommendations { review-id: review-id, recommendation-id: recommendation-id } (merge item { patient-approved: true, patient-approved-at: block-height }))
      )
      (ok true)
    )
  )
)

(define-public (finalize-review (review-id uint) (decision (string-ascii 256)))
  (let
    (
      (review (unwrap! (map-get? medication-reviews review-id) err-not-found))
      (last-recommendation-id (get last-recommendation-id review))
    )
    (begin
      (try! (assert-pharmacist))
      (asserts! (is-eq (get pharmacist review) tx-sender) err-unauthorized)
      (asserts! (is-eq (get status review) review-status-in-progress) err-invalid-status)
      (asserts! (> last-recommendation-id u0) err-consensus-required)
      (let ((last-item (unwrap! (map-get? recommendations { review-id: review-id, recommendation-id: last-recommendation-id }) err-not-found)))
        (asserts! (has-dual-recommendation-approval last-item) err-consensus-required)
      )
      (map-set medication-reviews review-id (merge review { status: review-status-completed, finalized-at: block-height, decision: decision }))
      (ok true)
    )
  )
)

(define-public (register-drug-interaction (drug-a uint) (drug-b uint) (severity uint) (significance (string-ascii 120)) (management (string-ascii 256)) (evidence-level uint))
  (begin
    (try! (assert-pharmacist))
    (asserts! (not (is-eq drug-a drug-b)) err-invalid-input)
    (map-set drug-interactions { drug-a: drug-a, drug-b: drug-b } { severity: severity, significance: significance, management: management, evidence-level: evidence-level, updated-at: block-height })
    (ok true)
  )
)

(define-public (update-interaction-severity (drug-a uint) (drug-b uint) (severity uint))
  (let ((item (unwrap! (map-get? drug-interactions { drug-a: drug-a, drug-b: drug-b }) err-not-found)))
    (begin
      (try! (assert-pharmacist))
      (map-set drug-interactions { drug-a: drug-a, drug-b: drug-b } (merge item { severity: severity, updated-at: block-height }))
      (ok true)
    )
  )
)

(define-read-only (check-interaction (drug-a uint) (drug-b uint))
  (map-get? drug-interactions { drug-a: drug-a, drug-b: drug-b })
)

(define-read-only (get-interaction-details (drug-a uint) (drug-b uint))
  (map-get? drug-interactions { drug-a: drug-a, drug-b: drug-b })
)

(define-public (create-therapy-regimen (patient principal) (current-meds (list 20 uint)) (goals (string-ascii 256)))
  (let ((regimen-id (var-get next-regimen-id)))
    (begin
      (try! (assert-pharmacist))
      (map-set therapy-regimens regimen-id { patient: patient, pharmacist: tx-sender, current-meds: current-meds, proposed-meds: current-meds, goals: goals, status: review-status-pending, implemented: false, created-at: block-height, implemented-at: u0 })
      (map-set regimen-approvals regimen-id { pharmacist-approved: false, patient-approved: false })
      (var-set next-regimen-id (+ regimen-id u1))
      (bump-regimen-count patient)
      (ok regimen-id)
    )
  )
)

(define-public (optimize-regimen (regimen-id uint) (proposed-meds (list 20 uint)) (goals (string-ascii 256)))
  (let ((regimen (unwrap! (map-get? therapy-regimens regimen-id) err-not-found)))
    (begin
      (try! (assert-pharmacist))
      (asserts! (is-eq (get pharmacist regimen) tx-sender) err-unauthorized)
      (map-set therapy-regimens regimen-id (merge regimen { proposed-meds: proposed-meds, goals: goals, status: review-status-in-progress }))
      (map-set regimen-approvals regimen-id { pharmacist-approved: false, patient-approved: false })
      (ok true)
    )
  )
)

(define-public (approve-regimen-change (regimen-id uint))
  (let
    (
      (regimen (unwrap! (map-get? therapy-regimens regimen-id) err-not-found))
      (approval (default-to { pharmacist-approved: false, patient-approved: false } (map-get? regimen-approvals regimen-id)))
    )
    (begin
      (asserts! (or (is-eq tx-sender (get pharmacist regimen)) (is-eq tx-sender (get patient regimen))) err-unauthorized)
      (if
        (is-eq tx-sender (get pharmacist regimen))
        (map-set regimen-approvals regimen-id (merge approval { pharmacist-approved: true }))
        (map-set regimen-approvals regimen-id (merge approval { patient-approved: true }))
      )
      (ok true)
    )
  )
)

(define-public (implement-changes (regimen-id uint) (patient-confirmed bool))
  (let
    (
      (regimen (unwrap! (map-get? therapy-regimens regimen-id) err-not-found))
      (approval (default-to { pharmacist-approved: false, patient-approved: false } (map-get? regimen-approvals regimen-id)))
    )
    (begin
      (try! (assert-pharmacist))
      (asserts! (is-eq (get pharmacist regimen) tx-sender) err-unauthorized)
      (asserts! patient-confirmed err-consensus-required)
      (asserts! (has-dual-regimen-approval approval) err-consensus-required)
      (map-set therapy-regimens regimen-id (merge regimen { current-meds: (get proposed-meds regimen), implemented: true, status: review-status-completed, implemented-at: block-height }))
      (ok true)
    )
  )
)

(define-public (track-adherence (patient principal) (regimen-id uint) (score uint))
  (begin
    (try! (assert-pharmacist))
    (asserts! (<= score u100) err-invalid-input)
    (map-set adherence-scores { patient: patient, regimen-id: regimen-id } { score: score, updated-at: block-height })
    (ok true)
  )
)

(define-public (schedule-counseling (patient principal) (topics (string-ascii 256)) (session-date uint))
  (let ((session-id (var-get next-session-id)))
    (begin
      (try! (assert-pharmacist))
      (map-set counseling-sessions session-id { patient: patient, pharmacist: tx-sender, topics: topics, materials: "", follow-up-required: false, session-date: session-date, understanding-score: u0, documented: false })
      (var-set next-session-id (+ session-id u1))
      (bump-session-count patient)
      (ok session-id)
    )
  )
)

(define-public (document-counseling (session-id uint) (materials (string-ascii 256)) (follow-up-required bool))
  (let ((session (unwrap! (map-get? counseling-sessions session-id) err-not-found)))
    (begin
      (try! (assert-pharmacist))
      (asserts! (is-eq (get pharmacist session) tx-sender) err-unauthorized)
      (map-set counseling-sessions session-id (merge session { materials: materials, follow-up-required: follow-up-required, documented: true }))
      (ok true)
    )
  )
)

(define-public (assign-education-materials (session-id uint) (materials (string-ascii 256)))
  (let ((session (unwrap! (map-get? counseling-sessions session-id) err-not-found)))
    (begin
      (try! (assert-pharmacist))
      (asserts! (is-eq (get pharmacist session) tx-sender) err-unauthorized)
      (map-set counseling-sessions session-id (merge session { materials: materials }))
      (ok true)
    )
  )
)

(define-public (track-understanding (session-id uint) (understanding-score uint))
  (let ((session (unwrap! (map-get? counseling-sessions session-id) err-not-found)))
    (begin
      (try! (assert-pharmacist))
      (asserts! (<= understanding-score u100) err-invalid-input)
      (asserts! (is-eq (get pharmacist session) tx-sender) err-unauthorized)
      (map-set counseling-sessions session-id (merge session { understanding-score: understanding-score }))
      (ok true)
    )
  )
)

(define-public (record-outcome (patient principal) (regimen-id uint) (metric-type (string-ascii 64)) (measurement uint) (assessed-at uint) (target-achieved bool))
  (let ((outcome-id (var-get next-outcome-id)))
    (begin
      (try! (assert-pharmacist))
      (map-set clinical-outcomes outcome-id { patient: patient, regimen-id: regimen-id, metric-type: metric-type, measurement: measurement, assessed-at: assessed-at, target-achieved: target-achieved, flagged: false })
      (var-set next-outcome-id (+ outcome-id u1))
      (bump-outcome-count patient)
      (ok outcome-id)
    )
  )
)

(define-public (assess-progress (outcome-id uint) (flag-issue bool))
  (let ((outcome (unwrap! (map-get? clinical-outcomes outcome-id) err-not-found)))
    (begin
      (try! (assert-pharmacist))
      (map-set clinical-outcomes outcome-id (merge outcome { flagged: flag-issue }))
      (if flag-issue
        (bump-issue-count (get patient outcome))
        true
      )
      (ok true)
    )
  )
)

(define-read-only (identify-issues (outcome-id uint))
  (let ((outcome (unwrap! (map-get? clinical-outcomes outcome-id) err-not-found)))
    (ok (get flagged outcome))
  )
)

(define-read-only (generate-report (patient principal))
  (ok (get-stats patient))
)

(define-read-only (get-review (review-id uint))
  (map-get? medication-reviews review-id)
)

(define-read-only (get-recommendation (review-id uint) (recommendation-id uint))
  (map-get? recommendations { review-id: review-id, recommendation-id: recommendation-id })
)

(define-read-only (get-regimen (regimen-id uint))
  (map-get? therapy-regimens regimen-id)
)

(define-read-only (get-regimen-approval (regimen-id uint))
  (map-get? regimen-approvals regimen-id)
)

(define-read-only (get-counseling-session (session-id uint))
  (map-get? counseling-sessions session-id)
)

(define-read-only (get-outcome (outcome-id uint))
  (map-get? clinical-outcomes outcome-id)
)

(define-read-only (get-adherence (patient principal) (regimen-id uint))
  (map-get? adherence-scores { patient: patient, regimen-id: regimen-id })
)

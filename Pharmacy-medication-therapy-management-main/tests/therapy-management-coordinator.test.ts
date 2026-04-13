import { Cl } from "@stacks/transactions"
import { describe, expect, it } from "vitest"

declare const simnet: any

const contractName = "therapy-management-coordinator"

describe("therapy-management-coordinator", () => {
  it("only owner can authorize pharmacist", () => {
    const accounts = simnet.getAccounts()
    const deployer = accounts.get("deployer")
    const wallet1 = accounts.get("wallet_1")
    const wallet2 = accounts.get("wallet_2")

    const failed = simnet.callPublicFn(
      contractName,
      "authorize-pharmacist",
      [Cl.principal(wallet1)],
      wallet2
    )
    expect(failed.result).toBeErr(Cl.uint(100))

    const ok = simnet.callPublicFn(
      contractName,
      "authorize-pharmacist",
      [Cl.principal(wallet1)],
      deployer
    )
    expect(ok.result).toBeOk(Cl.bool(true))
  })

  it("review state machine blocks invalid transition and requires dual approval to finalize", () => {
    const accounts = simnet.getAccounts()
    const deployer = accounts.get("deployer")
    const pharmacist = accounts.get("wallet_1")
    const patient = accounts.get("wallet_2")

    simnet.callPublicFn(
      contractName,
      "authorize-pharmacist",
      [Cl.principal(pharmacist)],
      deployer
    )

    const created = simnet.callPublicFn(
      contractName,
      "create-medication-review",
      [Cl.principal(patient), Cl.uint(1700000000)],
      pharmacist
    )
    expect(created.result).toBeOk(Cl.uint(1))

    const invalidStatus = simnet.callPublicFn(
      contractName,
      "update-review-status",
      [Cl.uint(1), Cl.uint(2)],
      pharmacist
    )
    expect(invalidStatus.result).toBeErr(Cl.uint(102))

    const moveToProgress = simnet.callPublicFn(
      contractName,
      "update-review-status",
      [Cl.uint(1), Cl.uint(1)],
      pharmacist
    )
    expect(moveToProgress.result).toBeOk(Cl.bool(true))

    const recommendation = simnet.callPublicFn(
      contractName,
      "propose-recommendation",
      [Cl.uint(1), Cl.stringAscii("adjust evening dose based on observation")],
      pharmacist
    )
    expect(recommendation.result).toBeOk(Cl.uint(1))

    const approvedByPatient = simnet.callPublicFn(
      contractName,
      "approve-recommendation",
      [Cl.uint(1), Cl.uint(1)],
      patient
    )
    expect(approvedByPatient.result).toBeOk(Cl.bool(true))

    const approvedByPharmacist = simnet.callPublicFn(
      contractName,
      "approve-recommendation",
      [Cl.uint(1), Cl.uint(1)],
      pharmacist
    )
    expect(approvedByPharmacist.result).toBeOk(Cl.bool(true))

    const finalized = simnet.callPublicFn(
      contractName,
      "finalize-review",
      [Cl.uint(1), Cl.stringAscii("confirmed by patient and pharmacist")],
      pharmacist
    )
    expect(finalized.result).toBeOk(Cl.bool(true))
  })

  it("implement-changes requires patient confirmation", () => {
    const accounts = simnet.getAccounts()
    const deployer = accounts.get("deployer")
    const pharmacist = accounts.get("wallet_3")
    const patient = accounts.get("wallet_4")

    simnet.callPublicFn(
      contractName,
      "authorize-pharmacist",
      [Cl.principal(pharmacist)],
      deployer
    )

    const regimen = simnet.callPublicFn(
      contractName,
      "create-therapy-regimen",
      [Cl.principal(patient), Cl.list([Cl.uint(101), Cl.uint(202)]), Cl.stringAscii("stabilize blood pressure")],
      pharmacist
    )
    expect(regimen.result).toBeOk(Cl.uint(1))

    const noConfirm = simnet.callPublicFn(
      contractName,
      "implement-changes",
      [Cl.uint(1), Cl.bool(false)],
      pharmacist
    )
    expect(noConfirm.result).toBeErr(Cl.uint(105))

    const pharmacistApprove = simnet.callPublicFn(
      contractName,
      "approve-regimen-change",
      [Cl.uint(1)],
      pharmacist
    )
    expect(pharmacistApprove.result).toBeOk(Cl.bool(true))

    const afterPharmacistApprove = simnet.callReadOnlyFn(
      contractName,
      "get-regimen-approval",
      [Cl.uint(1)],
      pharmacist
    )
    expect(afterPharmacistApprove.result).toBeSome(
      Cl.tuple({
        "pharmacist-approved": Cl.bool(true),
        "patient-approved": Cl.bool(false),
      })
    )

    const stillBlocked = simnet.callPublicFn(
      contractName,
      "implement-changes",
      [Cl.uint(1), Cl.bool(true)],
      pharmacist
    )
    expect(stillBlocked.result).toBeErr(Cl.uint(105))

    const patientApprove = simnet.callPublicFn(
      contractName,
      "approve-regimen-change",
      [Cl.uint(1)],
      patient
    )
    expect(patientApprove.result).toBeOk(Cl.bool(true))

    const afterPatientApprove = simnet.callReadOnlyFn(
      contractName,
      "get-regimen-approval",
      [Cl.uint(1)],
      pharmacist
    )
    expect(afterPatientApprove.result).toBeSome(
      Cl.tuple({
        "pharmacist-approved": Cl.bool(true),
        "patient-approved": Cl.bool(true),
      })
    )

    const confirmed = simnet.callPublicFn(
      contractName,
      "implement-changes",
      [Cl.uint(1), Cl.bool(true)],
      pharmacist
    )
    expect(confirmed.result).toBeOk(Cl.bool(true))
  })
})

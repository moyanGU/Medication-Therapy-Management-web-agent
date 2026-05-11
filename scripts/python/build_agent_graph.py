import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRAPHIFY_ROOT = ROOT / "graphify-5"
if str(GRAPHIFY_ROOT) not in sys.path:
    sys.path.insert(0, str(GRAPHIFY_ROOT))

from graphify.analyze import god_nodes, suggest_questions, surprising_connections
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.detect import detect
from graphify.export import to_json
from graphify.extract import extract
from graphify.report import generate


TARGETS = [
    ROOT / "src" / "services" / "assistantEngine.ts",
    ROOT / "src" / "services" / "pageAgentRuntime.ts",
    ROOT / "src" / "services" / "pageAgentService.ts",
    ROOT / "src" / "services" / "pageAgentShared.ts",
    ROOT / "src" / "services" / "sessionMemory.ts",
    ROOT / "src" / "services" / "toolRegistry.ts",
    ROOT / "src" / "services" / "restrictedPageController.ts",
    ROOT / "backend" / "apps" / "core" / "ai_page_agent.py",
    ROOT / "backend" / "apps" / "core" / "ai_session_memory.py",
    ROOT / "backend" / "apps" / "core" / "ai_medication.py",
    ROOT / "backend" / "apps" / "core" / "views_ai.py",
    ROOT / "backend" / "apps" / "core" / "agents" / "base.py",
    ROOT / "backend" / "apps" / "core" / "agents" / "memory_agent.py",
    ROOT / "backend" / "apps" / "core" / "agents" / "medication_agent.py",
    ROOT / "backend" / "apps" / "core" / "agents" / "soap_agent.py",
]


def main():
    out_dir = ROOT / "graphify-out"
    out_dir.mkdir(exist_ok=True)

    paths = [path for path in TARGETS if path.exists()]
    extraction = extract(paths, cache_root=ROOT)
    graph = build_from_json(extraction)
    communities = cluster(graph)
    cohesion = score_all(graph, communities)
    labels = {cid: f"Community {cid}" for cid in communities}
    gods = god_nodes(graph)
    surprises = surprising_connections(graph, communities)
    questions = suggest_questions(graph, communities, labels)
    detection_result = detect(ROOT)
    detection_result["warning"] = (
        "Agent graph report is limited to the current auto_agent-related chain, not the whole repo."
    )
    report = generate(
        graph,
        communities,
        cohesion,
        labels,
        gods,
        surprises,
        detection_result,
        {"input": 0, "output": 0},
        str(ROOT),
        suggested_questions=questions,
    )
    community_headings = len(re.findall(r"^### Community ", report, flags=re.MULTILINE))

    (out_dir / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    to_json(graph, communities, str(out_dir / "graph.json"), force=True)
    (out_dir / "agent-targets.json").write_text(
        json.dumps([str(path.relative_to(ROOT)) for path in paths], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "nodes": graph.number_of_nodes(),
                "edges": graph.number_of_edges(),
                "communities": community_headings,
                "report": str((out_dir / "GRAPH_REPORT.md").relative_to(ROOT)),
                "graph": str((out_dir / "graph.json").relative_to(ROOT)),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

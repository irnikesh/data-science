import json
from .tools import tool_search, tool_calculator, tool_sql, tool_chart, tool_miro_upload_image
from .prompts import SYSTEM_PROMPT, TOOL_DESC

THOUGHT_INSTRUCTIONS = """
When using a tool, return JSON as:
{"thought":"<why>","tool":"search","input":"<query>"}
or
{"thought":"<why>","tool":"calculator","input":"<expr>"}
If no tool is needed:
{"thought":"<why>","tool":"<none>","input":""}
End your final message with a complete Markdown report.
"""

def run_agent(llm, task: str, max_steps: int = 5, verbose: bool = True):
    transcript = []
    context = f"{SYSTEM_PROMPT}\n{TOOL_DESC}\nTask: {task}\n{THOUGHT_INSTRUCTIONS}"
    for step in range(max_steps):
        reply = llm.complete(context)
        transcript.append({"step": step+1, "raw": reply})
        # Try to extract JSON tool call (first JSON object found)
        start = reply.find("{")
        depth=0; end=-1
        for i,ch in enumerate(reply[start:], start):
            if ch=='{': depth+=1
            elif ch=='}':
                depth-=1
                if depth==0:
                    end=i
                    break
        tool_used = "<none>"
        tool_input = ""
        thought = ""
        if start != -1 and end != -1:
            try:
                payload = json.loads(reply[start:end+1])
                thought = payload.get("thought", "")
                tool_used = payload.get("tool", "<none>")
                tool_input = payload.get("input", "")
            except Exception:
                pass

        if verbose:
            print(f"[step {step+1}] thought: {thought} | tool: {tool_used}")

        tool_output = None
        if tool_used == "search" and tool_input:
            tool_output = tool_search(tool_input, max_results=6)
            # Append compact citation lines
            cites = "\\n".join(f"- [{r['title']}]({r['url']}) — {r['snippet'][:120]}..." for r in tool_output)
            context += f"\n[tool:search results]\\n{cites}\n"
        elif tool_used == "calculator" and tool_input:
            tool_output = tool_calculator(tool_input)
            context += f"\n[tool:calculator result] {tool_output}\n"
        elif tool_used == "sql" and tool_input:
            result = tool_sql(tool_input, limit=1000)
            context += f"\n[tool:sql result] {str(result)[:1500]}\n"
        elif tool_used == "chart" and tool_input:
            import json as _json
            try:
                params = _json.loads(tool_input)
            except Exception:
                params = {}
            result = tool_chart(params.get('table', {}), params.get('x',''), params.get('y',''), params.get('kind','bar'), params.get('title','Chart'), params.get('filename','chart.png'))
            context += f"\n[tool:chart result] {str(result)}\n"
        elif tool_used == "miro_upload_image" and tool_input:
            result = tool_miro_upload_image(tool_input)
            context += f"\n[tool:miro result] {str(result)}\n"
        else:
            # Assume final answer included
            break

        # Encourage model to synthesize with new info
        context += "Using the information above, refine your plan. If ready, produce the final Markdown report now.\n"

    final = llm.complete(context + "\nFinish with the final Markdown report only.")
    transcript.append({"final": final})
    return final, transcript

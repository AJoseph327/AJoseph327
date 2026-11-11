#!/usr/bin/env python3
"""Free self-hosted GitHub contribution animation for AJoseph327.
Generated from GitHub's contribution calendar; no synthetic contributions.
"""
import datetime as dt
import html
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

USERNAME = "AJoseph327"
OUTPUT = Path("assets/contribution-orbit.svg")
QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount contributionLevel }
        }
      }
    }
  }
}"""
LEVELS = {"NONE":0, "FIRST_QUARTILE":1, "SECOND_QUARTILE":2, "THIRD_QUARTILE":3, "FOURTH_QUARTILE":4}
COLORS = ("#202124", "#594321", "#947032", "#C69A4B", "#F5D787")

def calendar():
    token = os.environ["GH_TOKEN"]
    data = json.dumps({"query": QUERY, "variables": {"login": USERNAME}}).encode("utf-8")
    req = Request("https://api.github.com/graphql", data=data, method="POST",
                  headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                           "Accept": "application/vnd.github+json", "User-Agent":"github-profile-orbit"})
    with urlopen(req, timeout=30) as response:
        result = json.load(response)
    if result.get("errors"):
        raise RuntimeError("GitHub GraphQL error: " + str(result["errors"]))
    return result["data"]["user"]["contributionsCollection"]["contributionCalendar"]

def main():
    data = calendar()
    weeks = data["weeks"][-53:]
    stamps = []
    months = []
    for column, week in enumerate(weeks):
        for day in week["contributionDays"]:
            daydate = dt.date.fromisoformat(day["date"])
            row = (daydate.weekday() + 1) % 7
            x, y = 145 + 17 * column, 107 + 17 * row
            level = LEVELS.get(day["contributionLevel"], 0)
            stamps.append(f'<rect x="{x}" y="{y}" width="11" height="11" rx="2.5" fill="{COLORS[level]}"><title>{day["date"]}: {day["contributionCount"]} contributions</title></rect>')
            if daydate.day <= 7:
                label = daydate.strftime("%b")
                if not months or months[-1][0] != (daydate.year, daydate.month):
                    months.append(((daydate.year, daydate.month), x, label))
    labels = ''.join(f'<text x="{x}" y="96" font-size="12" fill="#B9A476">{html.escape(label)}</text>' for _,x,label in months)
    grid = ''.join(stamps)
    total = data["totalContributions"]
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="310" viewBox="0 0 1200 310" role="img" aria-label="{total} real GitHub contributions with animated golden jet">
<defs><linearGradient id="bg"><stop stop-color="#080A0F"/><stop offset="1" stop-color="#17120E"/></linearGradient><linearGradient id="gold"><stop stop-color="#8B642C"/><stop offset=".5" stop-color="#FFE095"/><stop offset="1" stop-color="#8B642C"/></linearGradient></defs>
<rect width="1200" height="310" rx="13" fill="url(#bg)" stroke="#594728"/>
<text x="40" y="40" fill="url(#gold)" font-family="Arial,Helvetica,sans-serif" font-weight="bold" letter-spacing="2" font-size="19">ACTIVITY CONSTELLATION</text>
<text x="1155" y="40" text-anchor="end" fill="#B5A486" font-family="Arial,Helvetica,sans-serif" font-size="13">{total:,} REAL CONTRIBUTIONS</text>
<path d="M25 66 H1175" stroke="#634A24" stroke-opacity=".55"/>
<g font-family="Arial,Helvetica,sans-serif">{labels}</g><g>{grid}</g>
<path id="track" d="M150 224 C310 242 480 251 615 218 S965 185 1115 194" fill="none" stroke="#D7AE52" stroke-opacity=".27" stroke-dasharray="3 10"/>
<g><path d="M -75 0 H -18" stroke="#D6A64F" stroke-width="3"/><path d="M-13 0L11 -7L7 -1L21 0L7 1L11 7Z" fill="#FFDB7F" stroke="#FFF1CA" stroke-width=".8"/><circle cx="-18" cy="0" r="3" fill="#FFF1CA"/>
<animateMotion dur="16s" repeatCount="indefinite" rotate="auto" path="M150 224 C310 242 480 251 615 218 S965 185 1115 194"/></g>
<path d="M40 282H1160" stroke="#5C4426"/><text x="42" y="299" fill="#B9A479" font-family="Arial,Helvetica,sans-serif" font-size="10" letter-spacing="2">AJ / 327 · ALWAYS IN ORBIT</text>
<text x="1160" y="299" fill="#B9A479" text-anchor="end" font-family="Arial,Helvetica,sans-serif" font-size="10">LIVE · {today}</text></svg>"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT} from {total} real contributions")

if __name__ == "__main__":
    main()

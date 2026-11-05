User interview - "Pulse" reporting tool (fictional example)
Date: October 17, 2026 - Duration: 30 min
Interviewer: UX researcher

Interviewer: Hi Karim, could you introduce yourself?

Karim: Hi. Karim Benali, I'm a data analyst at Fretto, a last-mile delivery startup, we're about forty people.

Interviewer: How do you use Pulse?

Karim: I build the dashboards for the ops teams and for our customers. And I do a lot of exports. Pulse is good for visualizing, but as soon as we want to combine it with our internal data, I export everything to CSV and move it into our data warehouse. I even wrote a script that pulls the export every night, because there's no API for it.

Interviewer: A script, okay. Can you tell me more?

Karim: It's a bit of a hack. It logs in with my account, downloads the CSV and pushes it into BigQuery. When Pulse changes something in the interface, it breaks. That happened to me twice this quarter.

Interviewer: And how reliable are the numbers, in your view?

Karim: The numbers are right, on my side I've never seen a discrepancy. But the definitions aren't clear. A "delay", is that relative to the promised slot or to the estimated time? It's not written anywhere. So each team interprets it its own way.

Interviewer: What would save you the most time?

Karim: A real API, clearly. Or at least a scheduled export to a bucket. And a glossary of the metrics right inside the tool.

Interviewer: How did the setup go?

Karim: Very fast for us, in one afternoon. We have devs, we connected the integration ourselves. I understand it would be harder for a company without a technical team.

Interviewer: And sharing with your customers?

Karim: We create guest accounts for them, but each guest counts as a paying user. We had to limit the number of customers who have access. It's a shame, that's exactly what they like the most.

Interviewer: Thank you Karim.

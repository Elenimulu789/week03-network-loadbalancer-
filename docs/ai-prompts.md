# AI assistance and prompt log

## Disclosure

AI assistance was used to prepare the Docker Compose setup, Nginx configuration, Python backend, QA script, diagram, and documentation. The review examples were generated intentionally to make configuration auditing visible; they are not evidence that a dangerous configuration was deployed. Runtime results must come from executing the project, not from AI predictions.

The prompts below summarize the assistance used in this project; they are not presented as a verbatim chat transcript. Add your own follow-up prompts and changes as you work through the lab.

| Goal | Generalized prompt | Review focus |
| --- | --- | --- |
| Plan the topology | Help me design a local Docker lab with a public bridge, an internal private bridge, a dual-homed Nginx gateway, and two stateless backends with unique IDs and health endpoints. | Which services join each network? |
| Review insecure examples | Provide a clearly labeled review example containing backend port publications and an incomplete retry policy. Explain how to correct it without running the unsafe example. | Host port leakage, network naming versus actual isolation |
| Verify load balancing | Explain Nginx's default round-robin behavior, service-name DNS, passive failure detection, and bounded retries for small GET requests. | Avoid invented directives and unsupported guarantees |
| Build meaningful QA | Help create a cross-platform script that counts ten responses, stops one backend, checks twenty requests, restores it, and tests the public/private boundary. | Check real statuses; do not hide failures with client retries |
| Check the explanation | Review the README for claims Docker does not guarantee, including Linux host access to bridge IPs and the difference between liveness and readiness. | State the actual security boundary |
| Prepare the video | Help organize a six-minute demonstration with simple language and real commands. | Demonstrate results rather than reciting expected output |

## Review notes to complete personally

- Configuration issue I inspected: ____________________
- Correction I verified: ____________________
- QA run and evidence file: ____________________
- Any additional AI help or manual edits: ____________________

AI-generated review notes and this preparation record do not replace the student's own audit, execution, and video demonstration.

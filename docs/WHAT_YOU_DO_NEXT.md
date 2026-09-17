# What you do next

1. **GitHub CLI authentication — optional repair.** The saved `gh` token is
   currently invalid. Run `gh auth login` if you need CLI API commands.
   Ordinary HTTPS Git pushes are verified independently; public materials need
   no login.
2. **Repository publication — done.** The public repository is
   https://github.com/dmetagame/nightbasis; `main` and both requested tags were
   pushed and their targets verified. The public production demo is
   https://nightbasis.vercel.app.
3. **Capture the Playbook mirror.** Follow `docs/PLAYBOOK_MIRROR.md` and save the
   screenshots in `reports/playbook/`. Hide account identifiers and balances.
   Keep the caption **“Negative control. Not the shipped product.”** Commit and
   push the screenshots without changing any strategy rule.
4. **Video — done.** Use `web/demo/desk-walkthrough.mp4`: a 110-second,
   subtitled walkthrough with the full Tesla `z=1.235711` visible. Narration
   and actual timing are in `web/demo/VOICEOVER.txt` and `web/demo/SHOT_LOG.md`.
   The video is also copied to `/home/rouma/Downloads/desk-walkthrough.mp4`.
5. **Post on X.** Copy the exact post from `docs/SUBMISSION_FINAL.md`, retain
   the live demo link, attach the video if appropriate, publish it, and paste the X
   post URL into the submission form. Keep `#BitgetHackathon` and `@Bitget_AI`
   unchanged.
6. **Submit before the safety deadline.** Open the
   [Google Form](https://forms.gle/GyWZCMCPocgJdJon6), copy the blocks from
   `docs/SUBMISSION_FINAL.md`, add the public repository/materials link and X
   URL, and submit before the safety target **2026-09-21 18:00 UTC+8**.
   The submission deadline supplied for the final audit is **2026-09-21 23:59 UTC+8**. Review the
   [S2 handbook](https://bitget-ai.gitbook.io/bitgetai_hackathons2) once more
   before sending. The university affiliation field and any Qwen-specific form
   are separate; complete them only if you want to and they apply to you.

Final check: open the repository in a logged-out browser, verify every judge
link works, and run `make demo-replay` from a fresh clone.

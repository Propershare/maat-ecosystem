# Mintier Cron Schedule (Test Mode)

Mode: test
Delivery target: origin (this chat)

## Daily jobs

1) Morning publish
- Schedule: `0 9 * * *`
- Purpose: send daily primary post draft

2) Afternoon publish
- Schedule: `0 15 * * *`
- Purpose: send secondary/adapted variant

3) Evening engagement check
- Schedule: `0 20 * * *`
- Purpose: report replies, mentions, unanswered items

## Promotion to live

When test outputs are approved:
- Change delivery from `origin` to explicit platform targets
- Keep same schedules initially for 7 days
- Review weekly metrics and adjust cadence

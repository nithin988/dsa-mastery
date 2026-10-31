#!/bin/bash
# Solution for the pg-slow-query lab.
D="$HOME/sys-lab/pglab"
export PATH="$(ls -d /usr/lib/postgresql/*/bin | head -1):$PATH"
psql -X -q -h "$D" -p 5546 -U learner shop -c "create index events_user_idx on events(user_id); analyze events;"
psql -X -At -h "$D" -p 5546 -U learner shop -c "explain select count(*) from events where user_id = 4242"

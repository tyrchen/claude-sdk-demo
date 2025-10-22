# Instructions

## Generate system prompt

Please help me generate a sophisticated system prompt for an agent that is expert of postgres and it could generate executable postgres database schema migration and seed data from user's app idea. The output should be in ./specs/system-prompt.md.

generated files output:

```
./migrations/<timestamp>_<short_description>.sql
./seeds/<timestamp>_<short_description>.sql
```

Each time the user provides their input, the agent should look at existing migrations and seeds and generate the new migration and seed based on the user's input.

The agent should review the generated migrations and seeds and make sure they are correct and executable.

After review, the agent should verify with the following command:

```
createdb <temp_db_name>_<timestamp>
sqlx migrate run -D <temp_db_name>_<timestamp>
psql -d <temp_db_name>_<timestamp> -f ./seeds/<timestamp>_<short_description>.sql
dropdb <temp_db_name>_<timestamp>
```

If the command is successful, the agent should return the success message.

If the command is not successful, the agent should review the error and fix the error and try again until the command is successful.

## Generate agent

You're a python expert. Please build a python app based on the spec in ./specs/0001-spec.md.

#! /usr/bin/env bash

# API URL & headers
URL="https://ub-sd-p2-2024-f8-api.onrender.com/api/v1"
H1="accept: application/json"
H2="Content-Type: application"

# Get token from first superuser (change USER & PWD)
USER=""
PWD=""
TOKEN=$(curl -X "POST" "${URL}/login/access-token" -H "${H1}" -H "${H2}/x-www-form-urlencoded" -d "username=${USER}&password=${PWD}" | \
grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\([^"]*\)"/\1/')

# Authenticate with this token in following commands (change TOKEN)
AUTH="Authorization: Bearer ${TOKEN}"
curl -X "POST" "${URL}/login/test-token" -H "${H1}" -H "${AUTH}"

# User creation (those without account)
curl -X "POST" "${URL}/users/" -H "${H1}" -H "${AUTH}" -H "${H2}/json" -d "{\"is_superuser\": true, \"password\": \".test_1dm3n!\", \"email\": \"test_admin@sd.ub.edu\"}"
curl -X "POST" "${URL}/users/" -H "${H1}" -H "${AUTH}" -H "${H2}/json" -d "{\"password\": \".test_5s2r!\", \"email\": \"test_user@sd.ub.edu\"}"
curl -X "POST" "${URL}/users/" -H "${H1}" -H "${AUTH}" -H "${H2}/json" -d "{\"password\": \".test_4rg1n3z2r!\", \"email\": \"test_organizer_user@sd.ub.edu\"}"

# Account creation (and users Rich/Poor)
curl -X "POST" "${URL}/account/" -H "${H1}" -H "${H2}/json" -d "{\"available_money\": 1000000, \"password\": \".test_r3ch!\", \"email\": \"test_rich_user@sd.ub.edu\"}"
curl -X "POST" "${URL}/account/" -H "${H1}" -H "${H2}/json" -d "{\"available_money\": 50, \"password\": \".test_p44r!\", \"email\": \"test_poor_user@sd.ub.edu\"}"

# Team creation
countries=("Australia" "USA" "France" "Germany" "Japan" "Canada")
TEAM_ID=10
for i in "${!countries[@]}"; do
    j=$((i+TEAM_ID))
    curl -X "PUT" "${URL}/teams/?team_id=${j}" -H "${H1}" -H "${AUTH}" -H "${H2}/json" -d "{\"name\": \"${countries[$i]}\", \"country\": \"${countries[$i]}\"}"
done

# Competition creation (without organizer)
COMP_ID=$(curl -X "POST" "${URL}/competitions/" -H "${H1}" -H "${AUTH}" -H "${H2}/json" -d \
"{\"name\": \"Paris Olympic Games\", \"category\": \"Senior\", \"sport\": \"Basketball\", \"teams\": [\"Australia\", \"USA\", \"France\", \"Germany\", \"Japan\", \"Canada\"]}" | \
grep -o '"id":[0-9]*' | sed 's/"id":\([0-9]*\)/\1/')
curl -X "POST" "${URL}/competitions/" -H "${H1}" -H "${AUTH}" -H "${H2}/json" -d "{\"name\": \"SD Empty Competition\", \"category\": \"Senior\", \"sport\": \"Basketball\"}"

# Match creation, it was not specified match hour should be specified
curl -X 'POST' "${URL}/matches/" -H "${H1}" -H "${AUTH}" -H "${H2}/json" -d \
"{\"date\": \"29/07/2024\", \"price\": 325, \"number_of_seats\": 100, \"competition_id\": ${COMP_ID}, \"local_id\": ${TEAM_ID}, \"visitor_id\": $((TEAM_ID+2))}"
curl -X 'POST' "${URL}/matches/" -H "${H1}" -H "${AUTH}" -H "${H2}/json" -d \
"{\"date\": \"29/07/2024\", \"price\": 632, \"number_of_seats\": 20, \"competition_id\": ${COMP_ID}, \"local_id\": $((TEAM_ID+1)), \"visitor_id\": $((TEAM_ID+3))}"
curl -X 'POST' "${URL}/matches/" -H "${H1}" -H "${AUTH}" -H "${H2}/json" -d \
"{\"date\": \"30/07/2024\", \"price\": 50, \"number_of_seats\": 3, \"competition_id\": ${COMP_ID}, \"local_id\": $((TEAM_ID+4)), \"visitor_id\": $((TEAM_ID+5))}"

timestamp_week_ago="$(date +'%s' --date '7 days ago')000000"

sqlite3 movies.db "delete from venues where revision < $timestamp_week_ago"
sqlite3 movies.db "delete from movies where revision < $timestamp_week_ago"
sqlite3 movies.db "delete from showings where revision < $timestamp_week_ago"
sqlite3 movies.db "vacuum"


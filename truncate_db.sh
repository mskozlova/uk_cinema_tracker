timestamp_week_ago="$(date +'%s')000000"

sqlite3 movies.db "delete from venues where revision < $timestamp_week_ago"
sqlite3 movies.db "delete from movies where revision < $timestamp_week_ago"
sqlite3 movies.db "delete from showings where revision < $timestamp_week_ago"
sqlite3 movies.db "vacuum"


from prometheus_client import Counter

user_created_counter = Counter("user_created", "Number of users created")
user_logged_in_counter = Counter("user_logged_in", "Number of user logins")
user_logged_out_counter = Counter("user_logged_out", "Number of user logouts")

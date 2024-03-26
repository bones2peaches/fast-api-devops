from prometheus_client import Counter

user_created_counter = Counter("user_created", "Number of users created")
user_logged_in_counter = Counter("user_logged_in", "Number of user logins")
user_logged_out_counter = Counter("user_logged_out", "Number of user logouts")
ws_connection_counter = Counter(
    "ws_connected", "Number of times a client connects to nchan"
)
ws_disconnection_counter = Counter(
    "ws_disconnected", "Number of times a client disconnects to nchan"
)

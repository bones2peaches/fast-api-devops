import http from "k6/http";
import { uuidv4 } from "https://jslib.k6.io/k6-utils/1.1.0/index.js";

class UserActions {
  constructor(
    domainName,
    protocol,
    stage,
    username = null,
    password = null,
    token = null,
    id = null,
    authHeaders = null
  ) {
    this.domainName = domainName;
    this.username = username || `user_${uuidv4()}`;
    this.password = password || `pass_${uuidv4()}`;
    this.token = token;
    this.id = id;
    this.protocol = protocol;
    this.stage = stage;
    this.authHeaders = authHeaders;
  }

  // Creates a new user
  create() {
    const url = `${this.protocol}://${this.domainName}/api/user`;
    const payload = JSON.stringify({
      username: this.username,
      password: this.password,
    });
    const headers = { "Content-Type": "application/json" };

    const res = http.post(url, payload, { headers: headers });

    if (res.status == 201) {
      this.id = res.json()["id"];
    }

    return res;
  }

  // Logs a user in
  login() {
    const url = `${this.protocol}://${this.domainName}/api/user/session`;
    const payload = JSON.stringify({
      username: this.username,
      password: this.password,
    });
    const headers = { "Content-Type": "application/json" };

    const res = http.post(url, payload, { headers: headers });
    const token = res.json()["access_token"];
    const params = {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    };

    this.authHeaders = params;

    this.token = token;
    return res;
  }

  // Logs a user out
  logout() {
    const url = `${this.protocol}://${this.domainName}/api/user/session`;

    const res = http.del(url, null, this.authHeaders); // Note: http.del(url, body, params) - body is set to null
    console.log(`Logout response status: ${res.status}, token: ${this.token}`);
    return res; // Return the actual response object
  }

  createChatroom(name, category) {
    const url = `${this.protocol}://${this.domainName}/api/chatroom`;
    const payload = JSON.stringify({
      name: name,
      category: category,
    });

    const res = http.post(url, payload, this.authHeaders);

    return res;
  }
}

export { UserActions };

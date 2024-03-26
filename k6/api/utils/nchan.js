import http from "k6/http";
import { uuidv4 } from "https://jslib.k6.io/k6-utils/1.1.0/index.js";

class NchanClient {
  constructor(domainName, protocol, authHeaders, token) {
    this.domainName = domainName;
    this.protocol = protocol;
    this.authHeaders = authHeaders;
    this.token = token;
  }

  updateChatroom(chatroomId) {
    const url = `${this.protocol}://${this.domainName}/api/chatroom/${chatroomId}/user?access_token=${this.token}`;

    const res = http.post(url, this.authHeaders);

    return res;
  }
}

export { NchanClient };

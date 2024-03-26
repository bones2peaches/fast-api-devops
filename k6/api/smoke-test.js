import { check, sleep } from "k6";
import { UserActions } from "./utils/user.js";
import { randomIntBetween } from "https://jslib.k6.io/k6-utils/1.2.0/index.js";
import { uuidv4 } from "https://jslib.k6.io/k6-utils/1.1.0/index.js";
import { NchanClient } from "./utils/nchan.js";

export let options = {
  vus: 1,
  duration: "1s", // Run 10 iterations in total, with 1 iteration per VU
  tags: {
    testName: "smoke-test",
  },
};

export default function () {
  const rand = randomIntBetween(1, 2);

  const user = new UserActions("localhost:5000", "http", "dev");
  const createUser = user.create();
  check(createUser, {
    "creating a user yielded a 201 status code": (r) => r.status === 201,
  });

  const userLogin = user.login();
  check(userLogin, {
    "logging a user yielded a 201 status code": (r) => r.status === 201,
  });
  if (rand === 1) {
    const userLogout = user.logout();

    check(userLogout, {
      "logging out a user yielded a 204 status code": (r) => r.status === 204,
    });
  }

  const chatroomName = `chatroom_${uuidv4()}`;
  const createChatroom = user.createChatroom(chatroomName, "testing");
  check(createChatroom, {
    "successful create a chatroom with a status code of 201": (r) =>
      r.status === 201,
  });

  const chatroomId = createChatroom.json()["id"];
  console.log(chatroomId);
  const nchan = new NchanClient(
    "localhost",
    "http",
    user.authHeaders,
    user.token
  );
  const joinChatroom = nchan.updateChatroom(chatroomId);
  console.log(joinChatroom.status);
  console.log(joinChatroom.body);
}

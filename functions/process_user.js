//@ts-check

import { FixUsermetadataName } from "./auth0.js";

export const handler = async (user, context) => {
  const updated = await FixUsermetadataName(user);
  const newName = updated.payload.user_metadata.name;
  const msg = "User processed: " + updated.user_id + " - " + newName;
  // console.log("> msg", JSON.stringify({ msg, updated }, null, 2));

  return {
    message: msg,
  };
};

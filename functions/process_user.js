//@ts-check

import { FixUsermetadataName } from "./auth0.js";

export const handler = async (user, context) => {
  const updated = await FixUsermetadataName(user);

  return {
    // updated: updated,
    message: "User processed: " + updated.user_id,
  };
};

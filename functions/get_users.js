import { getListOfUsersWithUndefined } from "./auth0.js";

export const handler = async (event, context) => {
  const userResponse = await getListOfUsersWithUndefined();
  const { users } = userResponse;
  return {
    ...userResponse,
  };
};

//@ts-check
import auth0Ins from "auth0";
import { to } from "await-to-js";

const ManagementClient = auth0Ins.ManagementClient;

const UNDEFINED = "undefined";
const stage = process.env.NUXT_STAGE || process.env.STAGE || "dev";
function GetAuth0TenantURL(stage = "dev") {
  if (stage === "prod") {
    return "linuxfoundation.auth0.com";
  }

  return `linuxfoundation-${stage}.auth0.com`;
}

const AUTH0_TENANT_URL = GetAuth0TenantURL(stage);

const domain = AUTH0_TENANT_URL;
const clientId =
  process.env.NUXT_AUTH0_ADMIN_CLIENT || process.env.AUTH0_ADMIN_CLIENT;
const clientSecret =
  process.env.NUXT_AUTH0_ADMIN_CLIENT_SECRET ||
  process.env.AUTH0_ADMIN_CLIENT_SECRET;

export const auth0 = new ManagementClient({
  domain,
  clientId,
  clientSecret,
});

export async function getListOfUsersWithUndefined() {
  const query = `user_metadata.name:"undefined undefined"`;
  const userList = await auth0.getUsers({
    q: query,
    sort: "created_at:-1",
    include_totals: "true",
    search_engine: "v3",
    page: 0,
    per_page: 50,
  });

  const users = userList.users.filter((u) => u.user_id.includes("auth0|"));

  return { ...userList, length: users.length, users, query };
}

/**
 * @param {User<AppMetadata, UserMetadata>} user
 **/
export async function FixUsermetadataName(user) {
  const { user_metadata = {}, user_id } = user;
  const newName = getFullName({
    firstname: user_metadata?.given_name,
    lastname: user_metadata?.family_name,
  });

  const payload = {
    user_metadata: {
      ...user_metadata,
      name: newName,
    },
  };

  console.log("> user_payload", { user: user.user_id, payload });
  return { user_id, payload, result: { err: null, updated: null } };

  const [err, updated] = await to(
    auth0.updateUser({ id: user.user_id }, payload)
  );

  return { user_id, payload, result: { err, updated } };
}

function getFullName({ firstname = "", lastname = "", defaultValue = "" }) {
  if (!firstname && !lastname) {
    return defaultValue;
  }

  if (!firstname) {
    return lastname;
  }

  if (!lastname) {
    return firstname;
  }

  const validName = `${firstname} ${lastname}`;

  if (validName.includes(UNDEFINED)) {
    return defaultValue;
  }

  return validName.trim();
}

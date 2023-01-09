function waitFor(ms) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve();
    }, ms);
  });
}

module.exports.handler = async (event, context) => {
  console.log("> process_users event", JSON.stringify({ event }, null, 2));
  const { name } = event || {};
  const random = Math.floor(Math.random() * 5) + 1;

  await waitFor(random);

  return {
    message: "User processed: " + name + " in " + random + " seconds",
  };
};

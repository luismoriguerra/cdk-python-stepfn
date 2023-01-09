// example of lambda function in nodejs

// const AWS = require("aws-sdk");
// const dynamoDb = new AWS.DynamoDB.DocumentClient();

function waitFor(ms) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve();
    }, ms);
  });
}

module.exports.handler = async (event, context) => {
  console.log("> get_users event", JSON.stringify({ data: event }, null, 2));
  await waitFor(5000);
  return {
    users: [
      { name: "John" },
      { name: "Jane" },
      { name: "Bob" },
      { name: "Alice" },
      { name: "Joe" },
      { name: "pepe" },
      { name: "pepa" },
      { name: "pepo" },
      { name: "pepi" },
      { name: "pepu" },
    ],
  };
};

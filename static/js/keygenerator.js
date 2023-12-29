//generator private and public key when user is registered
var crypto = window.crypto || window.msCrypto;

// Change the key to JSON string format
async function exportKey(k) {
  return JSON.stringify(await crypto.subtle.exportKey("jwk", k));
}

// Generator keys and reutrn public key
async function genKey() {
  const user_keys = await crypto.subtle.generateKey({name:"ECDH", namedCurve: "P-256"}, true, ["deriveKey"]);
  return user_keys;
}

async function run() {

  //Generator the key for the user
  const user_pub_key = await genKey()

  document.getElementById("user_public_key_id").value = await exportKey(user_pub_key.publicKey);
  document.getElementById("user_private_key_id").value = await exportKey(user_pub_key.privateKey);
}

run()
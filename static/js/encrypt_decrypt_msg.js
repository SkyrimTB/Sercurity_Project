//encrypt the message
var crypto = window.crypto || window.msCrypto;

function convertArrayBufferToBase64(arrayBuffer) {
  return btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
}

async function exportKey(k) {
  return JSON.stringify(await crypto.subtle.exportKey("jwk", k));
}

function convertBase64ToArrayBuffer(base64) {
  return (new Uint8Array(atob(base64).split('').map(char => char.charCodeAt()))).buffer;
}
function deriveSecretKey(privateKey, publicKey) {
    return crypto.subtle.deriveKey(
      {
        name: "ECDH",
        public: publicKey
      },
      privateKey,
      {
        name: "AES-GCM",
        length: 256
      },
      true,
      ["encrypt", "decrypt"]
    );
  }

//Get user private key store in the localStorage
async function encrypts_msg(username, iv, messages_need) {

    // Import public key
    const receiver_pubkey = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem("receiver_pk")), {name:"ECDH", namedCurve: "P-256"}, true, [])

    //get current user private key from localStorage
    const current_sekey = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem(username)), {name:"ECDH", namedCurve: "P-256"}, true, ["deriveKey"])
    
    // Get the shared key
    const encrypt_key = await deriveSecretKey(current_sekey, receiver_pubkey);
    
    let enc = new TextEncoder();

    var encoded = enc.encode(messages_need);

    return await window.crypto.subtle.encrypt(
        {
          name: "AES-GCM",
          iv: iv
        },
        encrypt_key,
        encoded
      ); 
}

//Get user private key store in the localStorage
async function decrypt_msg(message, iv) {

  var current_user = document.getElementById("current_user_name").innerHTML

  // Import public key
  const receiver_pubkey = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem("receiver_pk")), {name:"ECDH", namedCurve: "P-256"}, true, [])

  //get current user private key from localStorage
  const current_sekey = await crypto.subtle.importKey("jwk", JSON.parse(localStorage.getItem(current_user)), {name:"ECDH", namedCurve: "P-256"}, true, ["deriveKey"])
  
  // Get the shared key
  const encrypt_key = await deriveSecretKey(current_sekey, receiver_pubkey);

  return await window.crypto.subtle.decrypt(
      {
        name: "AES-GCM",
        iv: iv
      },
      encrypt_key,
      message
    );
}

function encrypt_msg(username, pub_key) {

    iv = window.crypto.getRandomValues(new Uint8Array(12));

    var messages_need = document.getElementById("messages").value

    var current_user = document.getElementById("current_user_name").innerHTML

    let test = encrypts_msg(current_user, iv, messages_need);

    test.then((val) => {

      var final_msg = {
      iv: convertArrayBufferToBase64(iv),
      encrypt_key: convertArrayBufferToBase64(val)
      }

      document.getElementById(username).getElementsByClassName("msg_encrypted")[0].value = JSON.stringify(final_msg);
    });  
}

//Get the receiver's username
var username = document.getElementById("CurrentOpen")

if (username != null) {
  username = document.getElementById("CurrentOpen").innerHTML
}

var temp_tab = document.getElementById(username)

//Get the current login username
var current_user = document.getElementById("current_user_name").innerHTML

if (temp_tab != null) {
  if (temp_tab.getElementsByClassName("receiver_pk") != null && temp_tab.getElementsByClassName("current_user_pk") != null) {
    
    //Get current reciver's public key
    var receiver_pk = temp_tab.getElementsByClassName("receiver_pk")[0].value
    localStorage.setItem("receiver_pk",receiver_pk);
    
    //Get all messages history and decrypt it
    if (temp_tab != null) {
      var temp = temp_tab.getElementsByClassName("msg_need_changed")
      
      if (temp != null) {
        
        for (let i = 0; i < temp.length; i++) {

          //Get encrypt messages and iv
          var encrypt_info = JSON.parse(temp[i].innerHTML)
          var iv = encrypt_info["iv"]
          var iv_rest = convertBase64ToArrayBuffer(iv)
          var encrypt_key = encrypt_info["encrypt_key"]
          var ret = convertBase64ToArrayBuffer(encrypt_key)
    
          var decrypt_msgs = decrypt_msg(ret, iv_rest)

          //Show the decrypt_msgs
          var enc = new TextDecoder();
          decrypt_msgs.then((val) => {temp[i].innerHTML = enc.decode(val)})
          .catch(function(err){
            console.error(err);
        });
        }
        
      }
      
    }
  }
  
}




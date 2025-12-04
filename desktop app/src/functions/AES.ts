import CryptoJS from "crypto-js";
import { readTextFile, writeTextFile, BaseDirectory} from '@tauri-apps/plugin-fs';
import { readFileAsBase64 } from "./files";

function encrypt(text:string, key :string) {
    return CryptoJS.AES.encrypt(text, key).toString()
}

function decrypt(encrypted:string, key:string) {
    try {
        return CryptoJS.AES.decrypt(encrypted, key).toString(CryptoJS.enc.Utf8);
    } catch (error) {
        return "";
    }
}

async function encryptFile(path:string, key:string, id:string) {
    const fileData = await readFileAsBase64(path);
    const cipher = encrypt(fileData, key);
    //const userData = localStorage.getItem('userData');
    writeTextFile(`items\\${id}.txt`, cipher, {baseDir: BaseDirectory.AppLocalData});
}

async function decryptFile(path:string, key:string) {
    const ciphertext = await readTextFile(path, {baseDir: BaseDirectory.AppLocalData});
    const plain = decrypt(ciphertext, key);
    return plain;
}

async function getDecipheredItem(id:string) {
    const cipher = await readTextFile(`items\\${id}.txt`, {baseDir: BaseDirectory.AppLocalData});
    const passwordCipher = await readTextFile('session.txt', {baseDir: BaseDirectory.AppLocalData});
    const password = decrypt(passwordCipher, localStorage.getItem('install')!);
    const plain = decrypt(cipher, password);
    const obj = JSON.parse(plain);
    return obj;
}

async function getDecipheredAttachment(id:string) {
    const cipher = await readTextFile(`items\\${id}.txt`, {baseDir: BaseDirectory.AppLocalData});
    const passwordCipher = await readTextFile('session.txt', {baseDir: BaseDirectory.AppLocalData});
    const password = decrypt(passwordCipher, localStorage.getItem('install')!);
    const plain = decrypt(cipher, password);
    return plain;
}

async function setCipheredItemTemp(obj:string) {
    let obj2 = JSON.parse(obj);
    const passwordCipher = await readTextFile('session.txt', {baseDir: BaseDirectory.AppLocalData});
    const password = decrypt(passwordCipher, localStorage.getItem('install')!);
    const plain = JSON.stringify(obj2);
    const cipher = encrypt(plain, password);
    await writeTextFile(`items\\${obj2.id}.txt`, cipher, {baseDir: BaseDirectory.AppLocalData});
    return 0;
}

async function setCipheredItem(obj:{id:any}) {
    const passwordCipher = await readTextFile('session.txt', {baseDir: BaseDirectory.AppLocalData});
    const password = decrypt(passwordCipher, localStorage.getItem('install')!);
    const plain = JSON.stringify(obj);
    const cipher = encrypt(plain, password);
    await writeTextFile(`items\\${obj.id}.txt`, cipher, {baseDir: BaseDirectory.AppLocalData});
    return 0;
}

export {encrypt, decrypt, encryptFile, decryptFile, getDecipheredItem, getDecipheredAttachment, setCipheredItemTemp, setCipheredItem}
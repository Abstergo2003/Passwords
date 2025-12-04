import { useEffect, useRef, useState } from "react"
import { readTextFile, writeTextFile, remove, mkdir, BaseDirectory, exists } from '@tauri-apps/plugin-fs';
import { getCurrentWindow } from '@tauri-apps/api/window';
import { decrypt, encrypt } from "../../functions/AES";
import { namesToImages, generalDataStructure, checkPasswordStandards } from "../../functions/globalStandards";
import { newFolder } from "../../functions/files";
import ItemElement from "../itemElement";
import { GlobalPassword } from "../globalPassword";

function Normal() {
  const [isFirst, setIsFirst] = useState("Input Your Password");
  const [category, setCategory] = useState("all");
  const [passwordValid, setPasswordValid] = useState(false);
  const passwordInputRef = useRef<HTMLInputElement | null>(null);
  const [query, setQuery] = useState("");
  const [queried, setQueried] = useState([]);

  useEffect(() => {
    const install = localStorage.getItem('install');
    if (!install) {
      setIsFirst('Create Password');
      firstRun();
    }
  }, []);

  useEffect(()=> {
    // @TODO write query function
    setQueried([])
  }, [query, category])

  async function firstRun() {
      console.log('data get');
      await newFolder('items');
      await writeTextFile('items\\generalData.json', JSON.stringify(generalDataStructure), {baseDir: BaseDirectory.AppLocalData});
  }

  const closeWindow = () => {
    const appWindow = getCurrentWindow();
    appWindow.close();
  }

  // TODO
  const searchItems = (query:string) => {
    setQuery(query);
  }

  // TODO
  const loadItems = () => {
    // @TODO set as all read items since it runs only once
    setQueried([])
  }


  const inputPassword = async () => {
    console.log("run");
    try {
      console.log("input password");
      const inputEl = passwordInputRef.current;
      if (!inputEl) {
        console.error("Password input not found");
        return;
      }
      const password = inputEl.value;
      if (localStorage.getItem('install') == null) {
        console.log("first");
        const date = new Date();
        const timestamp = date.getTime();
        localStorage.setItem('install', timestamp.toString());
        const passwordCipher = encrypt(password, timestamp.toString());
        const trydecrypt = encrypt('test encrypt', password);
        await writeTextFile('test.txt', trydecrypt, { baseDir: BaseDirectory.AppLocalData });
        await writeTextFile('session.txt', passwordCipher, { baseDir: BaseDirectory.AppLocalData });
        inputEl.value = "";
        (document.querySelector('.password')! as HTMLDivElement).style.left = '-1200px';
        console.log("moved");
        loadItems();
      } else {
        console.log("not first");
        const trydecrypt = await readTextFile('test.txt', { baseDir: BaseDirectory.AppLocalData });
        console.log(decrypt(trydecrypt, password));
        if (decrypt(trydecrypt, password) == "") {
          const span = (document.querySelector('.password span')! as HTMLSpanElement);
          span.innerText = 'Password is incorrect!!!';
          return;
        }
        const passwordCipher = encrypt(password, localStorage.getItem('install')!);
        await writeTextFile('session.txt', passwordCipher, { baseDir: BaseDirectory.AppLocalData });
        inputEl.value = "";
        (document.querySelector('.password')! as HTMLDivElement).style.left = '-1200px';
        console.log("moved");
        loadItems();
      }
    } catch (e) {
      console.error("inputPassword ERROR:", e);
    }
  };

  const handleOnInput = () => {
    const inputEl = passwordInputRef.current;
    console.log(inputEl);
    if (!inputEl) return;

    const password = inputEl.value;
    const result = checkPasswordStandards(password);

    // pokaż komunikat walidacji
    const span = document.querySelector('.password span');
    if (span) span.textContent = result;

    // ustaw stan — przycisk kontrolowany przez React
    setPasswordValid(result === "" && password.length > 0);
  };


  return (
    <div>
      <div className="options" data-tauri-drag-region>
        <button id="close" onClick={closeWindow}></button>
        <input type="text" placeholder="Search" onInput={(event)=> {
          const value = (event.target as HTMLInputElement).value;
          searchItems(value);
        }} />
        <button id="addPosition"></button>
        <button id="lockSession"></button>
        <button id="settings"></button>
      </div>
      <div className="categories">
          <span className="clicked" style={{backgroundImage: "url(basic_home.svg"}} onClick={()=> {setCategory("all")}}>All Items</span>
          <span style={{backgroundImage: "url(weather_star.svg)"}} onClick={()=> {setCategory("favourites")}}>Favourites</span>
        <p>Categories</p>
          <span style={{backgroundImage: "url(basic_world.svg)"}} onClick={()=> {setCategory("password")}}>Password</span>
          <span style={{backgroundImage: "url(ecommerce_creditcard.svg)"}} onClick={()=> {setCategory("creditCard")}}>Credit Card</span>
          <span style={{backgroundImage: "url(basic_eye.svg)"}} onClick={()=> {setCategory("identity")}}>Identity</span>
          <span style={{backgroundImage: "url(basic_postcard.svg)"}} onClick={()=> {setCategory("license")}}>License</span>
          <span style={{backgroundImage: "url(basic_todo.svg)"}} onClick={()=> {setCategory("notes")}}>Notes</span>
      </div>
      <div className="items">
        {queried.map((item) => {
          return <ItemElement key="0" image="" item={item}></ItemElement>
        })}
      </div>
      <div className="details">
        <div className="main-info">
          <img src="basic_ban.svg" />
          <span>Facebook</span>
          <span>radek_korszla@o2.pl</span>
          <button style={{right: "1vw", backgroundImage: "url(three-dots-vertical.svg)"}}></button>
          <button style={{right: "calc(2vw + 6vh)",  backgroundImage: "url(weather_star.svg)"}}></button>
        </div>

        <div className="fields">
        </div>

        <div className="attachments">
        </div>
      </div>

      <GlobalPassword 
        isFirst={isFirst}
        handleOnInput={handleOnInput}
        passwordInputRef={passwordInputRef}
        inputPassword={inputPassword}
        passwordValid={passwordValid}/>

      <div className="toastField">
      </div>
    </div>
  );
}

export default Normal
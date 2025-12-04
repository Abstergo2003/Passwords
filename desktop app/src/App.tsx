import "./styles/App.css";
import "./styles/fonts.css"
import Normal from "./elements/pages/normal";
import Attachment from "./elements/pages/attachment";
import { HashRouter, Routes, Route } from "react-router-dom";

function App() {

  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Normal />} />
        <Route path="/attach" element={<Attachment />} />
      </Routes>
    </HashRouter>
  );
}


export default App;

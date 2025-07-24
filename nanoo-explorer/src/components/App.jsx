import { BrowserRouter, Routes, Route } from "react-router-dom";
import BlockExplorer from "./components/BlockExplorer";
import BlockDetail from "./components/BlockDetail";
import TxDetail from "./components/TxDetail";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<BlockExplorer />} />
        <Route path="/block/:index" element={<BlockDetail />} />
        <Route path="/tx/:txid" element={<TxDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

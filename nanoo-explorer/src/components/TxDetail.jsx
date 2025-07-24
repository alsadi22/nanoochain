import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";

export default function TxDetail() {
  const { txid } = useParams();
  const [tx, setTx] = useState(null);

  useEffect(() => {
    fetch("http://localhost:5000/chain")
      .then(res => res.json())
      .then(data => {
        for (const block of data) {
          const found = block.transactions.find(t => t.id === txid);
          if (found) {
            setTx(found);
            break;
          }
        }
      });
  }, [txid]);

  return (
    <div>
      <h2>Transaction {txid}</h2>
      <pre>{JSON.stringify(tx, null, 2)}</pre>
    </div>
  );
}

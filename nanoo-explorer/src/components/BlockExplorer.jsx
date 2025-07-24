import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";

export default function BlockDetail() {
  const { index } = useParams();
  const [block, setBlock] = useState(null);

  useEffect(() => {
    fetch("http://localhost:5000/chain")
      .then(res => res.json())
      .then(data => {
        const b = data.find(b => b.index === parseInt(index));
        setBlock(b);
      });
  }, [index]);

  return (
    <div>
      <h2>Block #{index}</h2>
      <pre>{JSON.stringify(block, null, 2)}</pre>
    </div>
  );
}


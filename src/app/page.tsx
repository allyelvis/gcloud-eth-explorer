'use client';

import { useState } from 'react';
import { ethers } from 'ethers';

const GCLOUD_RPC = 'https://blockchain.googleapis.com/v1/projects/aenzbi-cloud/locations/us-central1/endpoints/ethereum-mainnet/rpc?key=AIzaSyCTkj44NjTgfFELMP89ufrmHeWnW6utbG8';

export default function Home() {
  const [address, setAddress] = useState('');
  const [balance, setBalance] = useState('');
  const [txs, setTxs] = useState<any[]>([]);
  const [error, setError] = useState('');

  const fetchWalletData = async () => {
    setError('');
    try {
      const provider = new ethers.JsonRpcProvider(GCLOUD_RPC);
      const bal = await provider.getBalance(address);
      setBalance(ethers.formatEther(bal));

      const history = await provider.getHistory(address);
      setTxs(history.slice(-10).reverse()); // last 10 txs
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <main className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">GCloud Ethereum Explorer</h1>

      <input
        type="text"
        className="w-full p-2 border mb-2"
        placeholder="Enter wallet address"
        value={address}
        onChange={e => setAddress(e.target.value)}
      />
      <button className="bg-blue-600 text-white px-4 py-2 rounded" onClick={fetchWalletData}>
        Track Wallet
      </button>

      {error && <p className="text-red-600 mt-2">{error}</p>}

      {balance && (
        <div className="mt-4">
          <p><strong>Balance:</strong> {balance} ETH</p>
        </div>
      )}

      {txs.length > 0 && (
        <div className="mt-4">
          <h2 className="text-lg font-semibold">Recent Transactions</h2>
          <ul className="space-y-2 mt-2">
            {txs.map(tx => (
              <li key={tx.hash} className="text-sm border p-2 rounded">
                <p><strong>Hash:</strong> <a href={`https://etherscan.io/tx/${tx.hash}`} target="_blank" className="text-blue-600 underline">{tx.hash.slice(0, 40)}...</a></p>
                <p><strong>From:</strong> {tx.from}</p>
                <p><strong>To:</strong> {tx.to}</p>
                <p><strong>Value:</strong> {ethers.formatEther(tx.value)} ETH</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </main>
  );
}

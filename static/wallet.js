import * as ethers from 'https://cdn.jsdelivr.net/npm/ethers@6.15.0/+esm';

const ZEN_ADDR = '0x00000000000000000000000000000000007a656e'; // hex of 'zen'
const INDEXER_URL = 'https://mainnet.zentra.dev';
const BASE_CHAIN_ID = 8453n; // Base
const RPC_URL = 'https://mainnet.base.org';

// --- DOM ELEMENTS ---
const connectButton = document.getElementById('connectButton');
const walletConnectDiv = document.getElementById('walletConnect');
const walletInfoDiv = document.getElementById('walletInfo');
const userAddressSpan = document.getElementById('userAddress');
const networkNameSpan = document.getElementById('networkName');
const networkSwitchPanel = document.getElementById('networkSwitchPanel');
const switchNetworkButton = document.getElementById('switchNetworkButton');

const tabTransfer = document.getElementById('tab-transfer');
const tabCustom = document.getElementById('tab-custom');
const contentTransfer = document.getElementById('content-transfer');
const contentCustom = document.getElementById('content-custom');

const transferButton = document.getElementById('transferButton');
const customJsonButton = document.getElementById('customJsonButton');
const transferResult = document.getElementById('transferResult');
const balanceList = document.getElementById('balance-list');

// --- STATE ---
let provider;
let signer;
let userAddress;

// --- FUNCTIONS ---

const showMessage = (message, type) => {
  console.log(`[${type}] ${message}`);
  if (transferResult) {
    const color = type === 'error' ? 'text-red-500' : 'text-green-500';
    transferResult.innerHTML = `<span class="${color} font-bold">${message}</span>`;
  }
};

const switchTab = (tab) => {
  if (tab === 'transfer') {
    tabTransfer.classList.add('text-blue-600', 'border-blue-600');
    tabTransfer.classList.remove('text-gray-500', 'border-transparent');
    tabCustom.classList.remove('text-blue-600', 'border-blue-600');
    tabCustom.classList.add('text-gray-500', 'border-transparent');
    contentTransfer.classList.remove('hidden');
    contentCustom.classList.add('hidden');
  } else {
    tabCustom.classList.add('text-blue-600', 'border-blue-600');
    tabCustom.classList.remove('text-gray-500', 'border-transparent');
    tabTransfer.classList.remove('text-blue-600', 'border-blue-600');
    tabTransfer.classList.add('text-gray-500', 'border-transparent');
    contentCustom.classList.remove('hidden');
    contentTransfer.classList.add('hidden');
  }
};

async function fetch_decimal(token) {
  try {
    const prefix = `base-${token}-decimal`;
    const url = `${INDEXER_URL}/api/get_latest_state?prefix=${encodeURIComponent(prefix)}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    return parseInt(data.result, 10);
  } catch (e) {
    console.error("Error fetching decimal:", e);
    return 18; // Default to 18 if failed
  }
}

async function fetch_token(token, address) {
  try {
    const prefix = `base-${token}-balance:${address.toLowerCase()}`;
    const url = `${INDEXER_URL}/api/get_latest_state?prefix=${encodeURIComponent(prefix)}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data_json = await response.text();

    const data = JSON.parse(data_json, (key, value, { source }) =>
      Number.isInteger(value) && !Number.isSafeInteger(value)
        ? BigInt(source)
        : value
    );

    let formatted_balance = '0';
    if (data.result) {
      const balance_big = BigInt(data.result);
      const decimal = await fetch_decimal(token);
      formatted_balance = ethers.formatUnits(balance_big, decimal);
    }

    const div = document.createElement('div');
    div.className = "flex justify-between";
    div.innerHTML = `<span>${token}</span> <span class="font-mono font-bold">${formatted_balance}</span>`;
    balanceList.appendChild(div);
  } catch (err) {
    console.error(`Fetch error for ${token}:`, err);
    // Still show the token with 0 balance on error
    const div = document.createElement('div');
    div.className = "flex justify-between";
    div.innerHTML = `<span>${token}</span> <span class="font-mono font-bold text-gray-400">Error</span>`;
    balanceList.appendChild(div);
  }
}

async function fetch_tx(txhash) {
  try {
    const url = `${INDEXER_URL}/api/events?txhash=${encodeURIComponent(txhash)}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const data = await response.json();
    console.log('response data:', data);

    // Check if events were found
    if (!data || (Array.isArray(data) && data.length === 0)) {
      console.log('No events found yet, retrying...');
      setTimeout(() => fetch_tx(txhash), 2000);
      return;
    }

    showMessage(`Transaction successful! <br> <a href="https://basescan.org/tx/0x${txhash}" target="_blank" class="underline">View on Explorer</a>`, 'success');

  } catch (err) {
    console.error('Fetch error:', err);
    showMessage(`Error checking transaction status: ${err.message}`, 'error');
  }
}

const checkNetwork = async () => {
  if (!provider) return false;
  const network = await provider.getNetwork();
  if (network.chainId !== BASE_CHAIN_ID) {
    if (networkSwitchPanel) networkSwitchPanel.style.display = 'flex';
    networkNameSpan.textContent = `Unsupported (${network.name})`;
    return false;
  } else {
    if (networkSwitchPanel) networkSwitchPanel.style.display = 'none';
    networkNameSpan.textContent = "Base";
    return true;
  }
};

const switchNetwork = async () => {
  if (!window.ethereum) return;
  try {
    await window.ethereum.request({
      method: 'wallet_switchEthereumChain',
      params: [{ chainId: `0x${BASE_CHAIN_ID.toString(16)}` }],
    });
  } catch (switchError) {
    if (switchError.code === 4902) {
      try {
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [{
            chainId: `0x${BASE_CHAIN_ID.toString(16)}`,
            chainName: 'Base',
            nativeCurrency: { name: 'ETH', symbol: 'ETH', decimals: 18 },
            rpcUrls: [RPC_URL],
            blockExplorerUrls: ['https://basescan.org']
          }]
        });
      } catch (addError) {
        console.error("Could not add network", addError);
      }
    }
  }
};

const connectWallet = async () => {
  if (typeof window.ethereum === 'undefined') {
    return showMessage('MetaMask is not installed!', 'error');
  }

  try {
    provider = new ethers.BrowserProvider(window.ethereum);
    await provider.send("eth_requestAccounts", []);
    signer = await provider.getSigner();
    userAddress = await signer.getAddress();

    walletInfoDiv.style.display = 'block';
    walletConnectDiv.style.display = 'none';
    userAddressSpan.textContent = userAddress;

    if (!await checkNetwork()) return;

    // Fetch balances
    if (balanceList) {
      balanceList.innerHTML = ''; // Clear previous
      // await fetch_token('BTC', userAddress);
      await fetch_token('USDC', userAddress);
      // await fetch_token('ZENT', userAddress);
    }

  } catch (error) {
    console.error(error);
    showMessage(`Error connecting wallet: ${error.message}`, 'error');
  }
};

const handleTransfer = async () => {
  const tick = document.getElementById('transfer_tick').value;
  const to = document.getElementById('transfer_to').value;
  const amountStr = document.getElementById('transfer_amount').value;

  if (!tick || !to || !amountStr) {
    return showMessage('Please fill in all fields', 'error');
  }

  try {
    transferButton.disabled = true;
    transferButton.innerText = "Processing...";

    const decimal = await fetch_decimal(tick);
    const amount = ethers.parseUnits(amountStr, decimal);

    const calldata = {
      "p": "zen",
      "f": "token_transfer",
      "a": [tick, to, amount.toString()],
    };

    const tx = await signer.sendTransaction({
      to: ZEN_ADDR,
      data: ethers.hexlify(new TextEncoder().encode(JSON.stringify(calldata)))
    });

    showMessage(`Transaction sent: ${tx.hash}`, 'success');
    fetch_tx(tx.hash.slice(2));

  } catch (error) {
    console.error(error);
    showMessage(`Transfer failed: ${error.message}`, 'error');
  } finally {
    transferButton.disabled = false;
    transferButton.innerText = "Transfer Token";
  }
};

const handleCustomJson = async () => {
  const jsonStr = document.getElementById('custom_json').value;
  if (!jsonStr) return showMessage('Please enter JSON', 'error');

  try {
    customJsonButton.disabled = true;
    customJsonButton.innerText = "Processing...";

    // Validate JSON
    JSON.parse(jsonStr);

    const tx = await signer.sendTransaction({
      to: ZEN_ADDR,
      data: ethers.hexlify(new TextEncoder().encode(jsonStr))
    });

    showMessage(`Transaction sent: ${tx.hash}`, 'success');
    fetch_tx(tx.hash.slice(2));

  } catch (error) {
    console.error(error);
    showMessage(`Failed: ${error.message}`, 'error');
  } finally {
    customJsonButton.disabled = false;
    customJsonButton.innerText = "Send Custom Call";
  }
};

// --- INITIALIZATION ---
const init = async () => {
  if (connectButton) connectButton.addEventListener('click', connectWallet);
  if (switchNetworkButton) switchNetworkButton.addEventListener('click', switchNetwork);

  if (tabTransfer) tabTransfer.addEventListener('click', () => switchTab('transfer'));
  if (tabCustom) tabCustom.addEventListener('click', () => switchTab('custom'));

  if (transferButton) transferButton.addEventListener('click', handleTransfer);
  if (customJsonButton) customJsonButton.addEventListener('click', handleCustomJson);

  // Snake game logic (preserved)
  const canvas = document.getElementById('snakeCanvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    const pixelSize = 12;
    let width, height, cols, rows;
    let score = 210000n;

    const resize = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
      cols = Math.floor(width / pixelSize);
      rows = Math.floor(height / pixelSize);
    }
    window.addEventListener('resize', resize);

    class Food {
      constructor() { this.respawn(); }
      draw() {
        const centerX = this.x * pixelSize + pixelSize / 2;
        const centerY = this.y * pixelSize + pixelSize / 2;
        const radius = pixelSize / 2;
        ctx.fillStyle = 'gold';
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = 'black';
        ctx.font = `${pixelSize * 0.7}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('Z', centerX, centerY);
      }
      respawn() {
        this.x = Math.floor(Math.random() * cols);
        this.y = Math.floor(Math.random() * rows);
      }
    }

    class Snake {
      constructor() {
        this.body = [{ x: 0, y: rows - 1 }];
        this.dx = 0; this.dy = -1;
      }
      move() {
        const head = { x: this.body[0].x + this.dx, y: this.body[0].y + this.dy };
        this.body.unshift(head);
        let ateFood = false;
        for (let i = foods.length - 1; i >= 0; i--) {
          if (head.x === foods[i].x && head.y === foods[i].y) {
            foods.splice(i, 1);
            score -= 1n;
            ateFood = true;
            break;
          }
        }
        if (!ateFood && this.body.length > 50) this.body.pop();

        if (Math.random() < 0.1) {
          const newDirection = Math.floor(Math.random() * 4);
          if (newDirection === 0 && this.dy !== 1) { this.dx = 0; this.dy = -1; }
          else if (newDirection === 1 && this.dy !== -1) { this.dx = 0; this.dy = 1; }
          else if (newDirection === 2 && this.dx !== 1) { this.dx = -1; this.dy = 0; }
          else if (newDirection === 3 && this.dx !== -1) { this.dx = 1; this.dy = 0; }
        }

        if (head.x < 0) head.x = cols - 1;
        if (head.x >= cols) head.x = 0;
        if (head.y < 0) head.y = rows - 1;
        if (head.y >= rows) head.y = 0;
      }
      draw() {
        ctx.fillStyle = 'rgba(0, 255, 0, 0.5)';
        this.body.forEach(segment => {
          ctx.fillRect(segment.x * pixelSize, segment.y * pixelSize, pixelSize, pixelSize);
        });
      }
    }

    const drawGrid = () => {
      ctx.strokeStyle = 'rgba(0, 255, 0, 0.1)';
      ctx.beginPath();
      for (let x = 0; x < cols; x++) { ctx.moveTo(x * pixelSize, 0); ctx.lineTo(x * pixelSize, height); }
      for (let y = 0; y < rows; y++) { ctx.moveTo(0, y * pixelSize); ctx.lineTo(width, y * pixelSize); }
      ctx.stroke();
    }

    const drawScore = () => {
      ctx.fillStyle = 'gold';
      ctx.font = '20px "Press Start 2P", monospace';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'bottom';
      ctx.fillText(`${score.toString()} ZTC`, 10, height - 10);
    }

    const animate = () => {
      ctx.clearRect(0, 0, width, height);
      drawGrid();
      snake.move();
      snake.draw();
      foods.forEach(food => food.draw());
      drawScore();
      setTimeout(animate, 100);
    }

    resize();
    const snake = new Snake();
    const foods = [];
    for (let i = 0; i < 100; i++) foods.push(new Food());
    animate();
  }

  // Mobile menu
  const mobileMenuButton = document.getElementById('mobile-menu-button');
  const mobileMenu = document.getElementById('mobile-menu');
  if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener('click', () => mobileMenu.classList.toggle('hidden'));
  }

  if (window.ethereum) {
    window.ethereum.on('chainChanged', () => window.location.reload());
    window.ethereum.on('accountsChanged', () => window.location.reload());
    const accounts = await window.ethereum.request({ method: 'eth_accounts' });
    if (accounts && accounts.length > 0) {
      await connectWallet();
    } else {
      walletConnectDiv.style.display = 'flex';
    }
  } else {
    walletConnectDiv.style.display = 'flex';
  }
};

document.addEventListener('DOMContentLoaded', init);

import bitcoin
from ecdsa import SigningKey, SECP256k1
from multiprocessing import Pool, cpu_count
import time

def generate_address(private_key_bytes):
    private_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)

    # Get the compressed public key
    public_key = private_key.get_verifying_key().to_string('compressed')

    # Generate a Bitcoin address from the compressed public key
    bitcoin_address = bitcoin.pubkey_to_address(public_key)
    return bitcoin_address

def generate_wallet(start_private_key, end_private_key):
    results = []
    for i in range(start_private_key, end_private_key+1):
        private_key = bytes.fromhex(hex(i)[2:].zfill(64))
        address = generate_address(private_key)
        results.append((private_key, address))
    return results

def generate_wallets(start_private_key, end_private_key, target_address):
    pool = Pool(processes=cpu_count())  # Use maximum available processes

    chunk_size = (end_private_key - start_private_key + 1) // pool._processes
    chunk_starts = range(start_private_key, end_private_key+1, chunk_size)
    chunk_ends = [min(start_private_key + (i+1) * chunk_size - 1, end_private_key) for i in range(pool._processes)]

    private_keys_chunks = [(chunk_starts[i], chunk_ends[i]) for i in range(pool._processes)]
    results = pool.starmap(generate_wallet, private_keys_chunks)
    pool.close()
    pool.join()

    for chunk_results in results:
        for private_key, address in chunk_results:
            if address == target_address:
                print("Matching private key found for address:", target_address)
                print("Private key:", private_key.hex())
                return

start_time = time.time()

start_private_key = 10000000000000
end_private_key = 10000000100000
target_address = "1Pie8JkxBT6MGPz9Nvi3fsPkr2D8q3GBc1"

if __name__ == '__main__':
    generate_wallets(start_private_key, end_private_key, target_address)

end_time = time.time()
execution_time = end_time - start_time

print("Execution Time:", execution_time, "seconds")

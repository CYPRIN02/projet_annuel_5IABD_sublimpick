<script>
  let query = '';
  let products = [];
  
  async function searchProducts() {
    if (query.length > 1) {
      const response = await fetch(`/search_products?query=${query}`);
      products = await response.json();
    }
  }
</script>

<main>
  <h1>Welcome to Sublimpick</h1>
  <p>Search for your favorite skincare products below:</p>
  
  <input type="text" bind:value={query} on:input={searchProducts} placeholder="Search for a product..." />

  <ul>
    {#each products as product}
      <li>
        <a href={`/product/${encodeURIComponent(product.product_link)}`}>
          {product.product_name}
        </a>
      </li>
    {/each}
  </ul>
</main>

<style>
  main {
    text-align: center;
    padding: 2em;
  }
  input {
    width: 100%;
    padding: 10px;
    margin-bottom: 20px;
  }
  ul {
    list-style-type: none;
    padding: 0;
  }
  li {
    margin: 10px 0;
  }
  a {
    text-decoration: none;
    color: #0070f3;
  }
</style>

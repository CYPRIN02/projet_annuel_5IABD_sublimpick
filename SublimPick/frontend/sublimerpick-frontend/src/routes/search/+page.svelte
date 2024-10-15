<script>
    let query = '';
    /**
     * @type {string | any[]}
     */
    let products = [];
  
    async function searchProducts() {
      if (query.length > 1) {
        const res = await fetch(`http://127.0.0.1:5000/search_products?query=${query}`);
        console.log(res);
        products = await res.json();
      }
    }
  </script>
  
  <main>
    <h1>Search for Products</h1>
  
    <input type="text" bind:value={query} on:input={searchProducts} placeholder="Type a product name..." />
  
    <ul>
      {#if products.length > 0}
        {#each products as product}
          <li>
            <a href={`/product/${encodeURIComponent(product.product_link)}`}>
              {product.product_name}
            </a>
            <!-- <a href={`/product/${product.product_link}`}>
              {product.product_name}
          </a> -->
          
          </li>
        {/each}
      {/if}
    </ul>
  </main>

  <style>
    main {
    padding: 40px;
  }

  input {
    width: 100%;
    padding: 12px;
    font-size: 16px;
    margin-bottom: 20px;
    border-radius: 5px;
    border: 1px solid #ccc;
  }

  ul {
    list-style-type: none;
    padding: 0;
  }

  li {
    margin-bottom: 10px;
  }

  a {
    color: #0070f3;
    text-decoration: none;
  }

  a:hover {
    text-decoration: underline;
}
  </style>

  

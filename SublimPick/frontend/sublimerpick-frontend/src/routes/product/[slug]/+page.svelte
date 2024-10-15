<script context="module">
  export async function load({ params }) {
    const product_url = decodeURIComponent(params.slug); // decoding the slug
    // const product_url = params.slug;
    console.log("Decoded product URL:", product_url);
    try {
      const response = await fetch(`http://127.0.0.1:5000/product_details?product_url=${product_url}`);
      console.log("API Response:", response);

      if (!response.ok) {
        throw new Error('Failed to fetch product details');
      }

      const product = await response.json(); // extract the response data
      return { props: { product } }; // pass product data to props
    } catch (error) {
      console.error('Error loading product details:', error);
      return {
        props: { product: null, error: error.message }
      };
    }
  }
</script>

<script>
  export let product;
  export let error;

  console.log('Product:', product);
  console.log('Error:', error);

  let isLoading = !product && !error;
</script>

<main>
  {#if isLoading}
    <p>Loading product details...</p>
  {:else if error}
    <p>There was an error loading the product details: {error}</p>
  {:else if product}
    <h1>{product.product_name}</h1>
    <p><strong>Price:</strong> {product.price}</p>
    <p><strong>Rating:</strong> {product.rating_star} stars ({product.rating_nb_reviews} reviews)</p>

    <h2>Customer Reviews</h2>
    {#if product.reviews && product.reviews.length > 0}
      <ul>
        {#each product.reviews as review}
          <li>
            <h3>{review.review_title}</h3>
            <p><strong>Author:</strong> {review.review_author}</p>
            <p><strong>Review:</strong> {review.review_thoughts}</p>
            <p><strong>Sentiment:</strong> {review.sentiment_category}</p>
            <p><strong>Sentiment Score:</strong> {review.predicted_sentiment}</p>
          </li>
        {/each}
      </ul>
    {:else}
      <p>No reviews available for this product.</p>
    {/if}
  {/if}
</main>

<style>
  main {
    padding: 40px;
  }

  ul {
    list-style-type: none;
    padding: 0;
  }

  li {
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #ccc;
  }

  h2 {
    margin-top: 40px;
  }

  h3 {
    margin: 0;
  }
</style>

<!-- 
<script context="module">
    export async function load({ params }) {
      const product_url = params.slug;
      const response = await fetch(`http://127.0.0.1:5000/product_details?product_url=${product_url}`);
      

      // If the response is not OK, throw an error
      if (!response.ok) {
        return {
          status: response.status,
          error: new Error(`Could not load product: ${response.statusText}`)
        };
      }

      const product = await response.json();
      return { props: { product } };
    }
  </script>
  
  <script>
    export let product;
  </script>
  
  <main>
    <h1>{product.product_name}</h1>
    <p>Price: {product.price}</p>
    <p>Rating: {product.rating_star} stars ({product.rating_nb_reviews} reviews)</p>
  
    <h2>Reviews</h2>
    {#if product.reviews.length > 0}
      <ul>
        {#each product.reviews as review}
          <li>
            <h3>{review.review_title}</h3>
            <p>By {review.review_author} on {review.review_date}</p>
            <p>{review.review_thoughts}</p>
            <p>Sentiment: {review.sentiment_category}</p>
          </li>
        {/each}
      </ul>
    {/if}
    {#if product.reviews.length == 0}
      <p>No reviews available for this product.</p>
    {/if}
  </main>
  
  <style>
    main {
      padding: 2em;
      max-width: 800px;
      margin: auto;
    }
    ul {
      list-style-type: none;
      padding: 0;
    }
    li {
      border-bottom: 1px solid #ccc;
      padding: 1em 0;
    }
    h3 {
      margin: 0;
    }
  </style>
   -->
<script>
	import '../app.css';
	import { Toast, initializeStores } from '@skeletonlabs/skeleton';

	initializeStores();
</script>

<svelte:head>
	<title>Haxball Cheat Detector</title>
</svelte:head>
<Toast />
<slot />

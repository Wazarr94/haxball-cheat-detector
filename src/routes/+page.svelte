<script lang="ts">
	import { handleFile } from '$lib/gameLogic';
	import { matchMinStore, type MatchMinStoreElement } from '$lib/matchStore';

	let matchesArr: MatchMinStoreElement;

	matchMinStore.subscribe((value) => {
		matchesArr = value;
	});

	async function getAnalysis() {
		const res = await fetch('api/recording', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(matchesArr)
		});
		const data = await res.json();
		console.log(data);
	}
</script>

<h1>Haxball Cheat Detector</h1>
<input type="file" accept=".hbr2" on:change={handleFile} />

{#if matchesArr.loading}
	<p>Loading...</p>
{:else if matchesArr.error}
	<p>Bad file</p>
{:else if matchesArr.matches.length > 0}
	<button on:click={getAnalysis}>Get analysis</button>
	{#each matchesArr.matches as match, index}
		<h3>Match {index + 1}</h3>
		<p>{match.scoreRed} - {match.scoreBlue}</p>
		<p>Actions for {match.playerActions.length} frames</p>
	{/each}
{/if}

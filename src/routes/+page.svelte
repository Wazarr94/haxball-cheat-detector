<script lang="ts">
	import { handleFile } from '$lib/gameLogic';
	import { matchStore, type MatchMinStoreElement, type MatchStoreElement } from '$lib/matchStore';

	let matchesArr: MatchStoreElement;
	let matchesMinArr: MatchMinStoreElement;

	matchStore.subscribe((value) => {
		matchesArr = value;
	});

	$: matchesMinArr = {
		loading: matchesArr.loading,
		error: matchesArr.error,
		matches: matchesArr.matches.map((match) => {
			return {
				scoreRed: match.scoreRed,
				scoreBlue: match.scoreBlue,
				gameTicks: match.gameTicks,
				playerActions: match.playerActions
			};
		})
	};

	async function getAnalysis() {
		const res = await fetch('api/recording', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(matchesMinArr)
		});
		const data = await res.json();
		console.log(data);
	}
</script>

<h1>Haxball Cheat Detector</h1>
<input type="file" accept=".hbr2" on:change={handleFile} />

{#if matchesMinArr.loading}
	<p>Loading...</p>
{:else if matchesMinArr.error}
	<p>Bad file</p>
{:else if matchesMinArr.matches.length > 0}
	<button on:click={getAnalysis}>Get analysis</button>
	{#each matchesMinArr.matches as match, index}
		<h3>Match {index + 1}</h3>
		<p>{match.scoreRed} - {match.scoreBlue}</p>
		<p>Actions for {match.playerActions.length} frames</p>
	{/each}
{/if}

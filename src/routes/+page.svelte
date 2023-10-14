<script lang="ts">
	import { getTime } from '$lib';
	import { handleFile } from '$lib/gameLogic';
	import {
		matchStore,
		type MatchMinStoreElement,
		type MatchStoreElement,
		type MatchElementMin
	} from '$lib/matchStore';

	let matchesArr: MatchStoreElement;
	let matchesMinArr: MatchMinStoreElement;

	matchStore.subscribe((value) => {
		matchesArr = value;
	});

	$: matchesMinArr = {
		loading: matchesArr.loading,
		error: matchesArr.error,
		matches: matchesArr.matches
			.filter((match) => match.gameTicks > 1)
			.map((match) => {
				return {
					scoreRed: match.scoreRed,
					scoreBlue: match.scoreBlue,
					gameTicks: match.gameTicks,
					playerActions: match.playerActions,
					suspiciousActions: []
				} satisfies MatchElementMin;
			})
	};

	async function getAnalysis() {
		let sendFile = JSON.stringify(matchesMinArr);
		let sizeOctetSendFile = new TextEncoder().encode(sendFile).length;
		let sizeMB = Math.round((sizeOctetSendFile / 1000000) * 100) / 100;
		console.log(`Size of file: ${sizeMB} MB`);

		const res = await fetch('api/recording', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(matchesMinArr)
		});
		const data = await res.json();
		console.log(data);
		let value = matchesMinArr.matches.map((match, index) => {
			return {
				...match,
				suspiciousActions: data.matches[index]
			} satisfies MatchElementMin;
		});
		matchesMinArr = {
			loading: false,
			error: false,
			matches: value
		} satisfies MatchMinStoreElement;
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
		{#if match.suspiciousActions}
			<p>Suspicious actions: {match.suspiciousActions.length}</p>
			<ul>
				{#each match.suspiciousActions as action}
					<li>
						{action.player} at {getTime(action.frame)} with pattern: {action.pattern.change_frame} frame
						actions for {action.pattern.consecutive_frames} frames (suspicion level: {action.pattern
							.suspicion})
					</li>
				{/each}
			</ul>
		{/if}
	{/each}
{/if}

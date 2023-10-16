<script lang="ts">
	import { getTime } from '$lib';
	import { handleFile } from '$lib/gameLogic';
	import {
		matchStore,
		type MatchMinStoreElement,
		type MatchStoreElement,
		type MatchElementMin,
		type SuspiciousAction
	} from '$lib/matchStore';
	import { compress } from 'brotli-compress';

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

	async function compressJSONStringify(jsonStr: string) {
		const file = new TextEncoder().encode(jsonStr);
		const quality = 3;
		const compressed = await compress(file, {
			quality: quality
		});
		return compressed;
	}

	async function getAnalysis() {
		let value = matchesMinArr.matches.map(async (match) => {
			const data = await sendMatch(match);
			return data;
		});

		let suspicions = await Promise.all(value);

		matchesMinArr = {
			loading: false,
			error: false,
			matches: [
				...matchesMinArr.matches.map((match, index) => {
					return {
						...match,
						suspiciousActions: suspicions[index].suspicions
					} satisfies MatchElementMin;
				})
			]
		} satisfies MatchMinStoreElement;
	}

	async function sendMatch(match: MatchElementMin): Promise<{ suspicions: SuspiciousAction[] }> {
		let sendFile = JSON.stringify(match);
		const compressedFile = await compressJSONStringify(sendFile);

		const res = await fetch('api/recording', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Content-Encoding': 'br'
			},
			body: compressedFile
		});
		return res.json();
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

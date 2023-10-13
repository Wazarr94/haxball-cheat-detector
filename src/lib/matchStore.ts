import { writable } from 'svelte/store';

type ShotMatch = {
	player: string;
	from: { x: number; y: number };
	to: { x: number; y: number };
};

type PlayerMatch = {
	id: number;
	nick: string;
	nation: string;
	goals: number;
	assists: number;
	kicks: number;
};

type MatchElement = {
	stadium: boolean;
	started: boolean;
	stopped: boolean;
	spaceMode: boolean;
	realSoccerMode: boolean;
	touches: string[];
	thirds: [number, number, number];
	changes: [string, string, string][];
	gameTicks: number;
	kicks: { player: string; x: number; y: number }[];
	shots: ShotMatch[];
	redTeam: string[];
	blueTeam: string[];
	shotsRed: number;
	shotsBlue: number;
	passes: string | ShotMatch;
	passesRed: number;
	passesBlue: number;
	kicksRed: number;
	kicksBlue: number;
	possRed: number;
	possBlue: number;
	scoreRed: number;
	scoreBlue: number;
	player: PlayerMatch[];
	goals: { scorer: string; assist: string | false; currentScore: [number, number] }[];
	playerActions: { frame: number; player: string; action: number }[][];
};

export type MatchStoreElement = {
	matches: MatchElement[];
	loading: boolean;
	error: boolean;
};

export const matchStore = writable<MatchStoreElement>({
	matches: [],
	loading: false,
	error: false
});

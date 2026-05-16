export interface FormState {
	email: string;
	password: string;
}

export type ReducerAction = {
	type: 'SET_VALUE';
	field: keyof FormState;
	value: FormState[keyof FormState];
};

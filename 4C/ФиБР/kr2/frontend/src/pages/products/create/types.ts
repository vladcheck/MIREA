export interface FormState {
	title: string;
	description: string;
	price: number;
	category: string;
}

export type FormAction = {
	[K in keyof FormState]: {
		type: 'SET_VALUE';
		field: K;
		value: FormState[K];
	};
}[keyof FormState];

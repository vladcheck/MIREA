export interface FormState {
	name: string;
	email: string;
	newPassword: string;
}

export type FormAction = {
	[K in keyof FormState]: {
		type: 'SET_VALUE';
		field: K;
		value: FormState[K];
	};
}[keyof FormState];

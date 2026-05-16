import type { UserRole } from "@root-shared/types/User";

type FieldName = string;
type ErrorMessage = string;
export type Errors = Record<FieldName, ErrorMessage>;

export interface FormState {
  email: string;
  firstName: string;
  lastName: string;
  password: string;
  submitPassword: string;
  roles: UserRole[];
  errors: Errors;
}

export type ReducerAction =
  | {
      [K in keyof FormState]: {
        type: "SET_VALUE";
        field: K;
        value: FormState[K];
      };
    }[keyof FormState]
  | {
      type: "SET_STATE";
      state: FormState;
    };

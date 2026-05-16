import { runInAction } from "mobx";
import { observer, useLocalObservable } from "mobx-react-lite";
import useApi from "@/features/api/hooks/useApi";
import FlexContainer from "@/shared/ui/FlexContainer";
import Input from "@/shared/ui/Input";
import LabelInputBlock from "@/shared/ui/LabelInputBlock";
import SubmitButton from "@/shared/ui/SubmitButton";

const FORM_ID = "reset-password-form";

const ForgotPasswordPage = observer(function ForgotPasswordPage() {
  const api = useApi();
  const state = useLocalObservable(() => ({
    name: "",
    email: "",
    newPassword: "",
  }));

  const onSubmit = async () => {
    await api.resetPassword(state);
  };

  return (
    <FlexContainer>
      <h1>Сброс пароля</h1>
      <form id={FORM_ID}>
        <LabelInputBlock label="Имя" htmlFor="name">
          <Input
            type="text"
            value={state.name}
            onChange={(e) => {
              runInAction(() => {
                state.name = e.target.value;
              });
            }}
            required
          />
        </LabelInputBlock>
        <LabelInputBlock label="Почта" htmlFor="email">
          <Input
            type="text"
            value={state.name}
            onChange={(e) => {
              runInAction(() => {
                state.email = e.target.value;
              });
            }}
            required
          />
        </LabelInputBlock>
        <LabelInputBlock label="Пароль" htmlFor="newPassword">
          <Input
            type="text"
            value={state.newPassword}
            onChange={(e) => {
              runInAction(() => {
                state.newPassword = e.target.value;
              });
            }}
            required
          />
        </LabelInputBlock>
      </form>
      <SubmitButton onClick={onSubmit} formId={FORM_ID}>
        Сбросить пароль
      </SubmitButton>
    </FlexContainer>
  );
});

export default ForgotPasswordPage;

import type { UserResponse } from "@root-shared/types/User";
import type { AxiosResponse } from "axios";
import { useEffect, useState } from "react";
import useApi from "@/features/api/hooks/useApi";
import useNotify from "@/features/notifications/useNotify";
import UserCardSmall from "@/shared/ui/UserCardSmall";

export default function AdminUsersPage() {
  const api = useApi();
  const notifier = useNotify();
  const [users, setUsers] = useState<UserResponse[]>([]);

  const onDeleteUser = (id: string) => {
    const result = confirm(
      "Вы точно хотите удалить этого пользователя? Это действие нельзя отменить!",
    );
    if (!result) return;
    api
      .deleteUserById(id)
      .then(() => {
        notifier.notifySuccess("Пользователь успешно удален.", 1000);
        setTimeout(() => window.location.reload(), 1000);
      })
      .catch((error: string) => notifier.notifyError(error));
  };

  useEffect(() => {
    api
      .getUsers()
      .then((response: AxiosResponse<UserResponse[]>) =>
        setUsers(response.data),
      )
      .catch((error: string) => notifier.notifyError(error));
  }, []);

  return (
    <main className="p-8 space-y-8 animate-in fade-in duration-700">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-text-color tracking-tight">
            Управление пользователями
          </h1>
          <p className="text-text-muted mt-1">
            Просмотр и администрирование всех зарегистрированных аккаунтов
          </p>
        </div>
        <div className="glass-panel px-6 py-3 border border-primary/20 bg-primary/5">
          <span className="text-text-muted text-sm uppercase tracking-wider font-bold">
            Всего пользователей
          </span>
          <div className="text-3xl font-black text-primary leading-none mt-1">
            {users.length}
          </div>
        </div>
      </header>

      {users.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {users.map((u) => (
            <UserCardSmall key={u.id} {...u} onDeleteUser={onDeleteUser} />
          ))}
        </div>
      ) : (
        <div className="glass-panel p-20 text-center text-text-muted italic border-dashed border-2">
          Пользователи не найдены. Попробуйте позже.
        </div>
      )}
    </main>
  );
}

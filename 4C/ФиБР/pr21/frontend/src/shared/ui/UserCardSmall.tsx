import type { UserResponse } from '@root-shared/types/User';
import { X } from 'lucide-react';
import Button from './Button';
import FlexContainer from './FlexContainer';

export default function UserCardSmall({
	onDeleteUser,
	...params
}: UserResponse & { onDeleteUser: (id: string) => void }) {
	return (
		<FlexContainer
			className="gap-4 glass-panel p-4 hover:bg-surface-hover transition-all duration-300 border border-border-color/50 shadow-sm"
			justify="between"
			align="center"
		>
			<FlexContainer className="gap-4" align="center">
				<div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-lg">
					{params.firstName[0]}
				</div>
				<div className="flex flex-col">
					<span className="font-bold text-text-color">
						{params.firstName} {params.lastName}
					</span>
					<span className="text-xs text-text-muted">{params.email}</span>
				</div>
			</FlexContainer>

			<FlexContainer className="gap-2" align="center">
				<div className="flex gap-1">
					{params.roles.map((role) => (
						<span
							key={role}
							className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
								role === 'admin'
									? 'bg-red-500/10 text-red-500 border border-red-500/20'
									: role === 'seller'
										? 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
										: 'bg-primary/10 text-primary border border-primary/20'
							}`}
						>
							{role}
						</span>
					))}
				</div>
				<Button
					onClick={() => onDeleteUser(params.id)}
					className="p-2 h-auto w-auto bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white rounded-lg transition-all border border-red-500/20"
					title="Удалить пользователя"
				>
					<X size={16} />
				</Button>
			</FlexContainer>
		</FlexContainer>
	);
}

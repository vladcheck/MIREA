import type { PropsWithChildren } from 'react';

export default function Footer({ children }: PropsWithChildren) {
	return <footer className="footer">{children}</footer>;
}

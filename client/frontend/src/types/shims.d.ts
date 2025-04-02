// 添加缺失的类型声明
declare module 'cookie' {
    export function parse(str: string, options?: any): Record<string, string>;
    export function serialize(name: string, value: string, options?: any): string;
}

declare module 'statuses' {
    const statuses: {
        (code: number): string;
        (message: string): number;
        [code: number]: string;
        [message: string]: number;
    };
    export default statuses;
}

declare module 'tough-cookie' {
    export class Cookie {
        constructor(properties?: any);
        key: string;
        value: string;
        expires: Date | null;
        domain: string | null;
        path: string | null;
        secure: boolean;
        httpOnly: boolean;
        extensions: string[] | null;
        creation: Date | null;
        creationIndex: number;

        // 方法
        toString(): string;
        cookieString(): string;
        static parse(cookieString: string, options?: any): Cookie | null;
    }

    export class CookieJar {
        constructor(store?: any, options?: any);
        setCookie(cookie: Cookie | string, url: string | URL, options?: any, cb?: (err: Error | null, cookie: Cookie) => void): Promise<Cookie>;
        getCookies(url: string | URL, options?: any, cb?: (err: Error | null, cookies: Cookie[]) => void): Promise<Cookie[]>;
        getCookieString(url: string | URL, options?: any, cb?: (err: Error | null, cookieString: string) => void): Promise<string>;
        getSetCookieStrings(url: string | URL, options?: any, cb?: (err: Error | null, cookies: string[]) => void): Promise<string[]>;
        removeAllCookies(cb?: (err: Error | null) => void): Promise<void>;
        serialize(cb?: (err: Error | null, serialized: any) => void): Promise<any>;
        static deserialize(serialized: any, store?: any, cb?: (err: Error | null, jar: CookieJar) => void): Promise<CookieJar>;
    }
} 
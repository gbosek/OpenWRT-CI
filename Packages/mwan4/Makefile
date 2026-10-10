include $(TOPDIR)/rules.mk

PKG_NAME:=mwan4
PKG_VERSION:=1.0.0
PKG_RELEASE:=18
PKG_LICENSE:=MIT
PKG_MAINTAINER:=MWAN4 Team
PKG_BUILD_DIR:=$(BUILD_DIR)/mwan4-claus778-$(PKG_VERSION)
PKG_BUILD_PARALLEL:=1
PKG_BUILD_DEPENDS:=rust/host

include $(INCLUDE_DIR)/package.mk
include $(TOPDIR)/feeds/packages/lang/rust/rust-package.mk

define Package/mwan4
  SECTION:=net
  CATEGORY:=Network
  TITLE:=MWAN4 Rust ECMP multi-WAN manager
  URL:=https://github.com/gbosek/claus778-mwan4
  DEPENDS:=@aarch64 $(RUST_ARCH_DEPENDS) +libc +ip-full
  CONFLICTS:=mwan3
endef

define Package/mwan4/conffiles
/etc/config/mwan4
endef

define Build/Prepare
	$(call Build/Prepare/Default)
	$(CP) ./src ./Cargo.toml ./Cargo.lock $(PKG_BUILD_DIR)/
endef

define Build/Configure
endef

define Package/mwan4/install
	$(INSTALL_DIR) $(1)/usr/bin $(1)/etc/init.d $(1)/etc/config
	$(INSTALL_BIN) $(PKG_INSTALL_DIR)/bin/mwan4 $(1)/usr/bin/mwan4
	$(INSTALL_BIN) ./files/etc/init.d/mwan4 $(1)/etc/init.d/mwan4
	$(INSTALL_CONF) ./files/etc/config/mwan4 $(1)/etc/config/mwan4
endef

$(eval $(call BuildPackage,mwan4))
